"""SNN CREP tensor for spiking-aeon Package 26."""

from __future__ import annotations

import math

from spiking_aeon.constants import ETA_SNN, GAMMA_SNN, SIGMA_CREP


class CREPSNN:
    """
    CREP tensor for the neuromorphic SNN domain.

    C = inter-neuron spike-time coherence (measured on-chip)
    R = stochastic resonance peak proximity (optimal noise level)
    E = collective computation emergence (task accuracy vs. random baseline)
    P = spike-train permutation entropy
    Γ = arctanh(η_SNN) / σ  where η_SNN = H*/K = 320/1000 = 0.32 → Γ ≈ 0.150
    """

    def __init__(
        self,
        C: float = 0.5,
        R: float = 0.6,
        E: float = 0.4,
        P: float = 0.6,
    ) -> None:
        self.C = C
        self.R = R
        self.E = E
        self.P = P

    @property
    def gamma(self) -> float:
        """Γ(t) from geometric mean of CREP components."""
        product = max(0.0, self.C * self.R * self.E * self.P)
        eta = product ** 0.25
        eta = min(eta, 0.9999)
        return math.atanh(eta) / SIGMA_CREP

    @property
    def gamma_reference(self) -> float:
        """Reference Γ_SNN = arctanh(0.32) / 2.2 ≈ 0.150."""
        return GAMMA_SNN

    def as_dict(self) -> dict[str, float]:
        return {
            "C": self.C,
            "R": self.R,
            "E": self.E,
            "P": self.P,
            "Gamma": self.gamma,
            "Gamma_ref": self.gamma_reference,
            "eta": ETA_SNN,
        }

    def update_from_simulation(
        self,
        spike_coherence: float,
        resonance_proximity: float,
        accuracy_vs_random: float,
        spike_entropy: float,
    ) -> None:
        self.C = spike_coherence
        self.R = resonance_proximity
        self.E = accuracy_vs_random
        self.P = spike_entropy
