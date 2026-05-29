"""Caspase-3/9 ultrasensitive activation cascade."""

from __future__ import annotations

from cellular_genesis.constants import (
    HILL_N,
    K_CASP_ACT,
    K_CASP_INH,
)


class CaspaseCascade:
    """
    Ultrasensitive caspase-3 activation (switch-like UTAC phase transition).

    d[casp]/dt = k_act * cytoc^n / (K_half^n + cytoc^n) * (1 - casp) - k_inh * casp
    Hill coefficient n ≈ 6 gives ultrasensitivity.
    casp ≈ 0 → cell survives; casp → 1 → irreversible commitment to death.
    """

    K_HALF = 0.3   # half-saturation for cytochrome c

    def __init__(self) -> None:
        self.caspase = 0.01   # initialise near zero
        self.committed = False

    def _hill(self, cytoc: float) -> float:
        num = cytoc ** HILL_N
        den = self.K_HALF ** HILL_N + cytoc ** HILL_N
        return num / den if den > 0 else 0.0

    def step(self, cytochrome_c: float, dt: float = 0.1) -> float:
        activation = K_CASP_ACT * self._hill(cytochrome_c) * (1.0 - self.caspase)
        inhibition = K_CASP_INH * self.caspase
        self.caspase += (activation - inhibition) * dt
        self.caspase = max(0.0, min(1.0, self.caspase))
        if self.caspase > 0.5:
            self.committed = True
        return self.caspase

    @property
    def emergence(self) -> float:
        """CREP E: switch-like emergence of the caspase cascade."""
        return self.caspase
