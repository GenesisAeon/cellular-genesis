"""Mitochondrial membrane potential and cytochrome c release model."""

from __future__ import annotations

import math


class MitochondriaModel:
    """
    Mitochondrial membrane potential Δψ and cytochrome c release.

    Δψ_norm ∈ [0, 1]: normalised membrane potential (1 = healthy, 0 = collapsed).
    Cytochrome c released when ATP < ATP_THRESHOLD and Δψ < Δψ_threshold.
    """

    DELTA_PSI_HEALTHY = 1.0
    DELTA_PSI_THRESHOLD = 0.3
    CYTOC_RELEASE_RATE = 0.5   # h⁻¹

    def __init__(self, delta_psi_init: float = 0.95) -> None:
        self.delta_psi = delta_psi_init
        self.cytochrome_c = 0.0   # released fraction [0, 1]

    def update(self, atp_normalised: float, dt: float = 0.1) -> dict[str, float]:
        """Update Δψ and cytochrome c based on current ATP level."""
        # Δψ tracks ATP with slight lag
        target_psi = atp_normalised
        self.delta_psi += (target_psi - self.delta_psi) * 0.3 * dt

        # cytochrome c release when Δψ below threshold
        if self.delta_psi < self.DELTA_PSI_THRESHOLD:
            release_rate = self.CYTOC_RELEASE_RATE * (1.0 - self.cytochrome_c)
            self.cytochrome_c = min(1.0, self.cytochrome_c + release_rate * dt)

        return {
            "delta_psi": self.delta_psi,
            "cytochrome_c": self.cytochrome_c,
        }

    @property
    def membrane_resonance(self) -> float:
        """CREP R-component: resonance of Δψ oscillation around threshold."""
        dist = abs(self.delta_psi - self.DELTA_PSI_THRESHOLD)
        return math.exp(-dist * 5.0)
