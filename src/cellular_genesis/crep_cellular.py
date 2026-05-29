"""Cellular CREP tensor for Package 25."""

from __future__ import annotations

import math

from cellular_genesis.constants import ETA_APOPTOSIS, GAMMA_CELLULAR, SIGMA_CREP


class CREPCellular:
    """
    CREP tensor for the apoptosis domain.

    C = Bcl-2/Bcl-xL coherence (anti-apoptotic network stability)
    R = mitochondrial membrane potential resonance (Δψ)
    E = caspase cascade emergence (ultrasensitive switch state)
    P = entropy of cell-to-cell ATP variability (population noise)
    Γ = arctanh(η) / σ  where η = H*/K = ATP_threshold/K_ATP = 0.20
    """

    def __init__(self, C: float = 0.6, R: float = 0.5, E: float = 0.1, P: float = 0.7) -> None:
        self.C = C
        self.R = R
        self.E = E
        self.P = P

    @property
    def gamma(self) -> float:
        """Γ(t) computed from geometric mean of CREP components."""
        product = max(0.0, self.C * self.R * self.E * self.P)
        eta = product ** 0.25  # geometric mean
        eta = min(eta, 0.9999)
        return math.atanh(eta) / SIGMA_CREP

    @property
    def gamma_reference(self) -> float:
        """Reference Γ_cellular = arctanh(η_apoptosis) / σ ≈ 0.090."""
        return GAMMA_CELLULAR

    def as_dict(self) -> dict[str, float]:
        return {
            "C": self.C,
            "R": self.R,
            "E": self.E,
            "P": self.P,
            "Gamma": self.gamma,
            "Gamma_ref": self.gamma_reference,
            "eta": ETA_APOPTOSIS,
        }

    def update_from_state(
        self,
        network_coherence: float,
        membrane_resonance: float,
        caspase_emergence: float,
        atp_entropy: float,
    ) -> None:
        self.C = network_coherence
        self.R = membrane_resonance
        self.E = caspase_emergence
        self.P = atp_entropy
