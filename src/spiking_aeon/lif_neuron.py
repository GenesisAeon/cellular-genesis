"""Leaky Integrate-and-Fire neuron model for spiking-aeon Package 26."""

from __future__ import annotations

import math

from spiking_aeon.constants import (
    DT_MS,
    R_MEMBRANE,
    TAU_M_MS,
    TAU_REF_MS,
    V_RESET,
    V_REST,
    V_THRESHOLD,
)


class LIFNeuron:
    """
    Single Leaky Integrate-and-Fire neuron.

    C·dV/dt = -(V - V_rest)/τ_m + R·I_total
    Fires when V > V_threshold; resets to V_reset for τ_ref.
    CREP modulates V_threshold: V_th(t) = V_th0 · (1 - tanh(σ·Γ))
    """

    def __init__(
        self,
        tau_m: float = TAU_M_MS,
        v_threshold: float = V_THRESHOLD,
        v_reset: float = V_RESET,
        tau_ref: float = TAU_REF_MS,
        r_mem: float = R_MEMBRANE,
    ) -> None:
        self.tau_m = tau_m
        self.v_threshold = v_threshold
        self.v_threshold_base = v_threshold
        self.v_reset = v_reset
        self.tau_ref = tau_ref
        self.r_mem = r_mem

        self.v = V_REST
        self._ref_countdown = 0.0
        self.spike_times: list[float] = []

    def apply_crep(self, gamma: float, sigma: float = 2.2) -> None:
        """Dynamically lower (less negative) threshold with high CREP → more responsive."""
        # v_threshold is negative; raising it toward 0 = easier to fire
        modulation = math.tanh(sigma * gamma)  # ∈ [0, 1)
        shift = abs(self.v_threshold_base) * modulation * 0.5
        self.v_threshold = self.v_threshold_base + shift

    def step(self, t: float, i_syn: float, i_noise: float = 0.0, dt: float = DT_MS) -> bool:
        """Advance one timestep. Returns True if neuron fired."""
        if self._ref_countdown > 0.0:
            self._ref_countdown -= dt
            return False

        i_total = i_syn + i_noise
        dv = (-(self.v - V_REST) / self.tau_m + self.r_mem * i_total / self.tau_m) * dt
        self.v += dv

        if self.v >= self.v_threshold:
            self.v = self.v_reset
            self._ref_countdown = self.tau_ref
            self.spike_times.append(t)
            return True
        return False

    @property
    def firing_rate_hz(self) -> float:
        """Mean firing rate [Hz] over recorded spike train."""
        n = len(self.spike_times)
        if n < 2:
            return 0.0
        duration_s = (self.spike_times[-1] - self.spike_times[0]) * 1e-3
        return (n - 1) / duration_s if duration_s > 0 else 0.0

    @property
    def isi_cv(self) -> float:
        """Coefficient of variation of inter-spike intervals (spike regularity)."""
        if len(self.spike_times) < 3:
            return 1.0
        isis = [
            self.spike_times[i + 1] - self.spike_times[i]
            for i in range(len(self.spike_times) - 1)
        ]
        mean = sum(isis) / len(isis)
        if mean == 0.0:
            return 0.0
        variance = sum((x - mean) ** 2 for x in isis) / len(isis)
        return math.sqrt(variance) / mean
