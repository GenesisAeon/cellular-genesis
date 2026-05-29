"""Brian2-compatible software simulation backend for spiking-aeon Package 26.

Uses pure Python/numpy LIF simulation when Brian2 is not installed.
Provides identical return format regardless of backend.
"""

from __future__ import annotations

import math
import random

from spiking_aeon.constants import (
    DT_MS,
    FIRING_RATE_MAX_HZ,
    N_EXCITATORY_FRAC,
    N_NEURONS_DEFAULT,
    V_THRESHOLD,
)
from spiking_aeon.lif_neuron import LIFNeuron
from spiking_aeon.stdp_plasticity import STDPRule


class Brian2Backend:
    """
    Pure-Python LIF network simulation (Brian2 software fallback).

    Simulates N_exc excitatory + N_inh inhibitory LIF neurons with random
    connectivity and Ornstein-Uhlenbeck current noise.  STDP learning is
    applied between excitatory neuron pairs.
    """

    def __init__(
        self,
        n_neurons: int = N_NEURONS_DEFAULT,
        weight_base: float = 0.5,
        tau_m_ms: float = 20.0,
        i_noise_amp: float = 0.15,
        tau_ref_ms: float = 2.0,
        connection_prob: float = 0.1,
        seed: int = 42,
    ) -> None:
        self.n_neurons = n_neurons
        self.weight_base = weight_base
        self.tau_m_ms = tau_m_ms
        self.i_noise_amp = i_noise_amp
        self.tau_ref_ms = tau_ref_ms
        self.connection_prob = connection_prob
        self.rng = random.Random(seed)

        n_exc = int(n_neurons * N_EXCITATORY_FRAC)
        self.neurons = [
            LIFNeuron(
                tau_m=tau_m_ms,
                v_threshold=V_THRESHOLD,
                tau_ref=tau_ref_ms,
            )
            for _ in range(n_neurons)
        ]
        self._is_excitatory = [i < n_exc for i in range(n_neurons)]

        # Sparse weight matrix: weights[(i, j)] = w for connection i → j
        self._weights: dict[tuple[int, int], float] = {}
        for i in range(n_neurons):
            for j in range(n_neurons):
                if i != j and self.rng.random() < connection_prob:
                    sign = 1.0 if self._is_excitatory[i] else -1.0
                    self._weights[(i, j)] = sign * weight_base * self.rng.uniform(0.5, 1.5)

        self._stdp = STDPRule()
        self._noise_state = [0.0] * n_neurons

    def run(
        self, duration_ms: float = 1000.0, dt: float = DT_MS
    ) -> dict[str, float | int | list[dict[str, object]]]:
        """Simulate network for duration_ms and return spike statistics."""
        steps = int(duration_ms / dt)
        t = 0.0
        phase_events: list[dict[str, object]] = []
        spike_counts = [0] * self.n_neurons
        prev_rate = 0.0

        for step in range(steps):
            spikes_this_step: list[int] = []

            # Compute synaptic input per neuron
            i_syn = [0.0] * self.n_neurons
            for (src, dst), w in self._weights.items():
                if self.neurons[src].spike_times:
                    last_spike = self.neurons[src].spike_times[-1]
                    if abs(t - last_spike) < dt * 2:
                        i_syn[dst] += w * 0.1

            for k, neu in enumerate(self.neurons):
                # OU noise
                tau_n = self.tau_m_ms
                sigma = self.i_noise_amp
                dx = (
                    -(self._noise_state[k]) / tau_n * dt
                    + sigma * math.sqrt(2.0 * dt / tau_n) * self.rng.gauss(0, 1)
                )
                self._noise_state[k] += dx

                fired = neu.step(t, i_syn=i_syn[k], i_noise=self._noise_state[k], dt=dt)
                if fired:
                    spikes_this_step.append(k)
                    spike_counts[k] += 1

            # STDP: update weights for co-active pairs
            if spikes_this_step and step % 10 == 0:
                for i in spikes_this_step:
                    for j in spikes_this_step:
                        if (i, j) in self._weights and i != j:
                            delta_t = 0.1  # same timestep → potentiation
                            self._weights[(i, j)] = self._stdp.update_weight(
                                self._weights[(i, j)], delta_t
                            )

            # Detect phase events: sudden firing rate jump > 30% in 10 ms window
            if step > 0 and step % int(10.0 / dt) == 0:
                window_rate = sum(spike_counts) / (self.n_neurons * 10e-3)
                if prev_rate > 0 and abs(window_rate - prev_rate) / prev_rate > 0.30:
                    phase_events.append(
                        {"t_ms": round(t, 2), "delta_rate_hz": round(window_rate - prev_rate, 2)}
                    )
                prev_rate = window_rate

            t += dt

        # Aggregate statistics
        total_spikes = sum(spike_counts)
        duration_s = duration_ms * 1e-3
        mean_rate_hz = total_spikes / (self.n_neurons * duration_s)
        active_fraction = sum(1 for c in spike_counts if c > 0) / self.n_neurons

        cvs = [n.isi_cv for n in self.neurons if len(n.spike_times) >= 3]
        mean_cv = sum(cvs) / len(cvs) if cvs else 1.0

        # Spike-time coherence: fraction of neurons firing within 1 ms windows
        spike_coherence = self._compute_coherence(duration_ms, dt)

        return {
            "mean_rate_hz": round(mean_rate_hz, 3),
            "active_fraction": round(active_fraction, 4),
            "mean_isi_cv": round(mean_cv, 4),
            "spike_coherence": round(spike_coherence, 4),
            "total_spikes": total_spikes,
            "phase_events": phase_events,
            "normalised_rate": round(mean_rate_hz / FIRING_RATE_MAX_HZ, 4),
        }

    def _compute_coherence(self, duration_ms: float, dt: float) -> float:
        """
        Measure spike-time coherence as normalised cross-correlation peak.
        Simplified: fraction of neuron pairs with at least one co-spike < 1 ms apart.
        """
        sample_size = min(100, self.n_neurons)
        sample = self.neurons[:sample_size]
        coherent_pairs = 0
        total_pairs = 0
        for i in range(len(sample)):
            for j in range(i + 1, min(i + 10, len(sample))):
                total_pairs += 1
                t_i = {round(t / 1.0) for t in sample[i].spike_times}
                t_j = {round(t / 1.0) for t in sample[j].spike_times}
                if t_i & t_j:
                    coherent_pairs += 1
        return coherent_pairs / total_pairs if total_pairs > 0 else 0.0
