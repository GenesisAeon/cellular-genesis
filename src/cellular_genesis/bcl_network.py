"""Bcl-2/Bcl-xL anti-apoptotic protein network."""

from __future__ import annotations

from cellular_genesis.constants import BCL_RESCUE_MAX, BCL_XL_DEFAULT, K_BCL


class BclNetwork:
    """
    Bcl-2/Bcl-xL anti-apoptotic network stability model.
    High Bcl-xL → suppresses cytochrome c release → shifts ATP threshold down.
    CREP C-component: coherence of the Bcl-2 protective network.
    """

    def __init__(self, bcl_xl: float = BCL_XL_DEFAULT, bcl2: float = 0.4) -> None:
        self.bcl_xl = bcl_xl   # Bcl-xL expression [0, 1]
        self.bcl2 = bcl2       # Bcl-2 expression [0, 1]
        self.bax = 0.1         # pro-apoptotic Bax [0, 1]

    @property
    def network_coherence(self) -> float:
        """CREP C: anti-apoptotic protein network stability."""
        anti = (self.bcl_xl + self.bcl2) / 2.0
        pro = self.bax
        return max(0.0, min(1.0, anti - pro))

    def activate_bax(self, cytochrome_c: float, dt: float = 0.1) -> None:
        """Cytochrome c activates Bax (positive feedback to apoptosis)."""
        self.bax = min(1.0, self.bax + cytochrome_c * 0.2 * dt)

    def rescue_fraction(self) -> float:
        """Fractional shift of ATP threshold from Bcl-xL expression."""
        return BCL_RESCUE_MAX * (self.bcl_xl / K_BCL)
