"""ODE model for intracellular ATP dynamics."""

from __future__ import annotations

import math
import random

from cellular_genesis.constants import (
    ATP_INITIAL_MM,
    ATP_THRESHOLD_MM,
    BCL_RESCUE_MAX,
    BCL_XL_DEFAULT,
    K_ATP,
    K_BCL,
    LOADING_RATE_R,
    SIGMA_ATP_NOISE,
    V_CONSUMPTION,
    V_GLYCOLYSIS,
    V_LEAK,
    V_OXPHOS_MAX,
)


class ATPDynamicsModel:
    """
    ODE model for intracellular ATP dynamics.

    dATP/dt = v_OXPHOS(O2) + v_glycolysis - v_consumption - v_leak
    ATP drops below H_threshold → cytochrome c release begins.
    Bcl-xL shifts threshold: H_threshold → H_threshold * (1 - Bcl_xL/K_bcl * BCL_RESCUE_MAX)
    """

    def __init__(
        self,
        atp_init: float = ATP_INITIAL_MM,
        bcl_xl: float = BCL_XL_DEFAULT,
        o2_fraction: float = 1.0,
        seed: int = 42,
    ) -> None:
        self.atp = atp_init
        self.bcl_xl = bcl_xl
        self.o2_fraction = o2_fraction
        self._rng = random.Random(seed)
        self.history: list[dict] = []

    @property
    def h_threshold(self) -> float:
        """Effective ATP threshold, shifted down by Bcl-xL expression."""
        rescue = BCL_RESCUE_MAX * (self.bcl_xl / K_BCL)
        return ATP_THRESHOLD_MM * (1.0 - rescue)

    def _v_oxphos(self) -> float:
        return V_OXPHOS_MAX * self.o2_fraction * (self.atp / K_ATP)

    def step(self, dt: float = 0.1, stress: float = 0.0) -> float:
        """Euler step of ATP ODE. stress ∈ [0,1] increases consumption."""
        v_prod = self._v_oxphos() + V_GLYCOLYSIS
        v_cons = V_CONSUMPTION * (1.0 + stress) + V_LEAK
        noise = self._rng.gauss(0.0, SIGMA_ATP_NOISE * dt)
        d_atp = (v_prod - v_cons + LOADING_RATE_R * (K_ATP - self.atp) / K_ATP) * dt + noise
        self.atp = max(0.0, min(K_ATP, self.atp + d_atp))
        return self.atp

    def is_below_threshold(self) -> bool:
        return self.atp < self.h_threshold

    def normalised(self) -> float:
        """H(t) = ATP / K_ATP ∈ [0, 1]."""
        return self.atp / K_ATP

    def run(self, duration_hours: float, dt: float = 0.1, stress: float = 0.0) -> list[dict]:
        t = 0.0
        self.history = []
        while t < duration_hours:
            atp = self.step(dt, stress)
            self.history.append({"t": round(t, 4), "atp": atp, "h": self.normalised()})
            t += dt
        return self.history
