"""Stochastic resonance optimiser for spiking-aeon Package 26."""

from __future__ import annotations

import math
import random

from spiking_aeon.constants import (
    D_NOISE_MAX,
    D_NOISE_MIN,
    D_NOISE_OPTIMAL,
    DT_MS,
    DURATION_MS_DEFAULT,
    TAU_M_MS,
)


def _ornstein_uhlenbeck_step(
    x: float, mu: float, sigma: float, tau: float, dt: float, rng: random.Random
) -> float:
    """One step of the Ornstein-Uhlenbeck noise process."""
    dx = -(x - mu) / tau * dt + sigma * math.sqrt(2.0 * dt / tau) * rng.gauss(0, 1)
    return x + dx


class StochasticResonanceOptimizer:
    """
    Finds the optimal noise amplitude D_res for the SNN (Ferreira 2025).

    Sweeps noise amplitude D and measures mean ISI-CV across neurons.
    Coherence resonance (CR) = minimum CV at D_res → maps to CREP R-component.
    """

    def __init__(
        self,
        n_neurons: int = 50,
        duration_ms: float = DURATION_MS_DEFAULT,
        dt: float = DT_MS,
        seed: int = 42,
    ) -> None:
        self.n_neurons = n_neurons
        self.duration_ms = duration_ms
        self.dt = dt
        self.rng = random.Random(seed)

    def _simulate_cv(self, noise_amp: float) -> float:
        """Return mean ISI-CV for a population under given noise amplitude."""
        from spiking_aeon.lif_neuron import LIFNeuron

        neurons = [LIFNeuron(tau_m=TAU_M_MS) for _ in range(self.n_neurons)]
        noise_state = [0.0] * self.n_neurons
        t = 0.0
        steps = int(self.duration_ms / self.dt)

        for _ in range(steps):
            for k, neu in enumerate(neurons):
                noise_state[k] = _ornstein_uhlenbeck_step(
                    noise_state[k], 0.0, noise_amp, TAU_M_MS, self.dt, self.rng
                )
                neu.step(t, i_syn=0.02, i_noise=noise_state[k], dt=self.dt)
            t += self.dt

        cvs = [n.isi_cv for n in neurons if len(n.spike_times) >= 3]
        return sum(cvs) / len(cvs) if cvs else 1.0

    def sweep(self, n_steps: int = 20) -> dict[str, object]:
        """
        Sweep noise amplitudes and return (D_res, min_CV, sweep_results).
        D_res is the amplitude that minimises ISI-CV (= coherence resonance peak).
        """
        d_values = [
            D_NOISE_MIN + (D_NOISE_MAX - D_NOISE_MIN) * i / (n_steps - 1)
            for i in range(n_steps)
        ]
        cv_values = [self._simulate_cv(d) for d in d_values]

        min_cv = min(cv_values)
        d_res = d_values[cv_values.index(min_cv)]

        return {
            "D_res": d_res,
            "min_CV": round(min_cv, 4),
            "D_optimal_ref": D_NOISE_OPTIMAL,
            "sweep_D": [round(d, 4) for d in d_values],
            "sweep_CV": [round(c, 4) for c in cv_values],
        }

    def resonance_r_component(self, d_res: float | None = None) -> float:
        """
        CREP R-component: proximity of operating point to optimal noise level.
        R = 1 - |D_actual - D_res| / D_res
        """
        target = d_res if d_res is not None else D_NOISE_OPTIMAL
        d_actual = D_NOISE_OPTIMAL
        return max(0.0, 1.0 - abs(d_actual - target) / target)
