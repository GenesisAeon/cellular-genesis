"""CREP tensor → LIF network parameter translation for spiking-aeon Package 26."""

from __future__ import annotations

from spiking_aeon.constants import (
    D_NOISE_OPTIMAL,
    TAU_M_MS,
    TAU_REF_MS,
    WEIGHT_INIT,
)


class CREPtoWeightMapper:
    """
    Translates CREP tensor Γ(C, R, E, P) to LIF / Loihi 2 network parameters.

    C → τ_m: high C = long membrane time constant = coherent temporal integration
    R → I_noise amplitude: high R = near-optimal stochastic resonance level
    E → synaptic weight base W: high E = stronger collective coupling
    P → τ_ref: high P = longer refractory period = richer temporal coding
    """

    def __init__(
        self,
        tau_m_range: tuple[float, float] = (5.0, 50.0),
        w_range: tuple[float, float] = (0.1, 1.0),
        tau_ref_range: tuple[float, float] = (1.0, 5.0),
        noise_range: tuple[float, float] = (0.01, 0.40),
    ) -> None:
        self.tau_m_range = tau_m_range
        self.w_range = w_range
        self.tau_ref_range = tau_ref_range
        self.noise_range = noise_range

    def _scale(self, value: float, lo: float, hi: float) -> float:
        return lo + value * (hi - lo)

    def translate(self, crep: dict[str, float]) -> dict[str, float]:
        """
        Return a full LIF network config dict from a CREP state dict.
        Keys: tau_m_ms, i_noise_amp, weight_base, tau_ref_ms, gamma_applied.
        """
        c = crep.get("C", 0.5)
        r = crep.get("R", 0.5)
        e = crep.get("E", 0.5)
        p = crep.get("P", 0.5)
        gamma = crep.get("Gamma", 0.15)

        tau_m = self._scale(c, *self.tau_m_range)
        i_noise_amp = self._scale(r, *self.noise_range)
        weight_base = self._scale(e, *self.w_range)
        tau_ref = self._scale(p, *self.tau_ref_range)

        return {
            "tau_m_ms": round(tau_m, 3),
            "i_noise_amp": round(i_noise_amp, 4),
            "weight_base": round(weight_base, 4),
            "tau_ref_ms": round(tau_ref, 3),
            "gamma_applied": round(gamma, 4),
        }

    def default_config(self) -> dict[str, float]:
        """Return LIF config matching Loihi 2 default operating point (Γ ≈ 0.150)."""
        return {
            "tau_m_ms": TAU_M_MS,
            "i_noise_amp": D_NOISE_OPTIMAL,
            "weight_base": WEIGHT_INIT,
            "tau_ref_ms": TAU_REF_MS,
            "gamma_applied": 0.150,
        }
