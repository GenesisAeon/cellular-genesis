"""Cell population model with ATP variability."""

from __future__ import annotations

import math
import random
import statistics

from cellular_genesis.atp_dynamics import ATPDynamicsModel
from cellular_genesis.bcl_network import BclNetwork
from cellular_genesis.caspase_cascade import CaspaseCascade
from cellular_genesis.constants import (
    BCL_XL_DEFAULT,
    DURATION_HOURS,
    N_CELLS_DEFAULT,
    SIGMA_ATP_NOISE,
)
from cellular_genesis.mitochondria import MitochondriaModel


class CellPopulation:
    """
    Population of N cells with stochastic ATP variability.
    Tracks survival fraction and population-level CREP entropy.
    """

    def __init__(
        self,
        n_cells: int = N_CELLS_DEFAULT,
        bcl_xl: float = BCL_XL_DEFAULT,
        seed: int = 42,
    ) -> None:
        self.n_cells = n_cells
        self.bcl_xl = bcl_xl
        rng = random.Random(seed)
        # Each cell gets a slightly different initial ATP
        self._cells = [
            {
                "atp": ATPDynamicsModel(
                    atp_init=4.5 + rng.gauss(0, SIGMA_ATP_NOISE),
                    bcl_xl=bcl_xl,
                    seed=seed + i,
                ),
                "mito": MitochondriaModel(),
                "bcl": BclNetwork(bcl_xl=bcl_xl),
                "casp": CaspaseCascade(),
                "alive": True,
            }
            for i in range(n_cells)
        ]
        self.phase_events: list[dict] = []

    def step(self, t: float, dt: float, stress: float = 0.0) -> None:
        for idx, cell in enumerate(self._cells):
            if not cell["alive"]:
                continue
            atp = cell["atp"].step(dt, stress)
            mito_state = cell["mito"].update(cell["atp"].normalised(), dt)
            cell["bcl"].activate_bax(mito_state["cytochrome_c"], dt)
            casp = cell["casp"].step(mito_state["cytochrome_c"], dt)
            if cell["casp"].committed and cell["alive"]:
                cell["alive"] = False
                self.phase_events.append({"t": t, "cell_id": idx, "atp": atp, "caspase": casp})

    def survival_fraction(self) -> float:
        alive = sum(1 for c in self._cells if c["alive"])
        return alive / self.n_cells

    def atp_entropy(self) -> float:
        """Permutation entropy proxy: std of ATP levels across population."""
        atps = [c["atp"].atp for c in self._cells if c["alive"]]
        if len(atps) < 2:
            return 0.0
        sigma = statistics.stdev(atps)
        # Normalise to [0, 1] via logistic
        return 1.0 / (1.0 + math.exp(-sigma))

    def run(
        self, duration_hours: float = DURATION_HOURS, dt: float = 0.5, stress: float = 0.0
    ) -> list[dict]:
        results = []
        t = 0.0
        while t < duration_hours:
            self.step(t, dt, stress)
            results.append(
                {
                    "t": round(t, 2),
                    "survival": self.survival_fraction(),
                    "entropy": self.atp_entropy(),
                }
            )
            t += dt
        return results
