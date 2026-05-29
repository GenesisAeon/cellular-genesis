"""Spike-Timing Dependent Plasticity for spiking-aeon Package 26."""

from __future__ import annotations

import math

from spiking_aeon.constants import STDP_LR, TAU_STDP_MS


class STDPRule:
    """
    Symmetric STDP: weight change depends on relative spike timing Δt = t_post - t_pre.

    ΔW = +A_plus · exp(-|Δt| / τ)  if Δt > 0  (post after pre → potentiation)
    ΔW = -A_minus · exp(-|Δt| / τ) if Δt < 0  (pre after post → depression)
    """

    def __init__(
        self,
        lr: float = STDP_LR,
        tau_ms: float = TAU_STDP_MS,
        a_plus: float = 1.0,
        a_minus: float = 1.05,
        w_min: float = 0.0,
        w_max: float = 1.0,
    ) -> None:
        self.lr = lr
        self.tau_ms = tau_ms
        self.a_plus = a_plus
        self.a_minus = a_minus
        self.w_min = w_min
        self.w_max = w_max

    def dw(self, delta_t_ms: float) -> float:
        """Compute weight change for spike timing difference Δt [ms]."""
        if delta_t_ms > 0:
            return self.lr * self.a_plus * math.exp(-delta_t_ms / self.tau_ms)
        elif delta_t_ms < 0:
            return -self.lr * self.a_minus * math.exp(delta_t_ms / self.tau_ms)
        return 0.0

    def update_weight(self, w: float, delta_t_ms: float) -> float:
        """Apply STDP rule and clip to [w_min, w_max]."""
        return max(self.w_min, min(self.w_max, w + self.dw(delta_t_ms)))
