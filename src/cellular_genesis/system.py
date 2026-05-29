"""CellularGenesis — Diamond Interface for Package 25."""

from __future__ import annotations

import math
import time

from cellular_genesis.bcl_network import BclNetwork
from cellular_genesis.caspase_cascade import CaspaseCascade
from cellular_genesis.constants import (
    ATP_THRESHOLD_MM,
    BCL_XL_DEFAULT,
    DURATION_HOURS,
    GAMMA_CELLULAR,
    K_ATP,
    LOADING_RATE_R,
    N_CELLS_DEFAULT,
    SIGMA_CREP,
)
from cellular_genesis.crep_cellular import CREPCellular
from cellular_genesis.mitochondria import MitochondriaModel
from cellular_genesis.population import CellPopulation
from cellular_genesis.resource_governor import ComputationalApoptosisGovernor


class CellularGenesis:
    """
    Diamond interface for Package 25 — Apoptosis / ATP Threshold UTAC system.

    H(t)  = intracellular ATP level / K_ATP  (normalised, [0, 1])
    H*    = ATP_threshold / K_ATP = 0.20
    Γ     ≈ 0.090  (cellular fragility index)

    Mandatory Diamond contract:
      run_cycle, get_crep_state, get_utac_state, get_phase_events, to_zenodo_record
    """

    PACKAGE_NUMBER = 25
    DOMAIN = "cell-biology"
    REFERENCE_DOI = "10.3389/fcell.2025.1611055"

    def __init__(
        self,
        n_cells: int = N_CELLS_DEFAULT,
        bcl_xl: float = BCL_XL_DEFAULT,
        seed: int = 42,
    ) -> None:
        self.n_cells = n_cells
        self.bcl_xl = bcl_xl
        self.seed = seed
        self._crep = CREPCellular()
        self._population: CellPopulation | None = None
        self._run_results: list[dict[str, float]] = []
        self._governor = ComputationalApoptosisGovernor()
        self._run_meta: dict[str, object] = {}

    def run_cycle(
        self,
        n_cells: int = N_CELLS_DEFAULT,
        duration_hours: float = DURATION_HOURS,
        stress: float = 0.0,
        dt: float = 0.5,
    ) -> dict[str, object]:
        """Run one simulation cycle over `duration_hours` for `n_cells` cells."""
        t_start = time.perf_counter()
        self._population = CellPopulation(
            n_cells=n_cells, bcl_xl=self.bcl_xl, seed=self.seed
        )
        self._run_results = self._population.run(duration_hours, dt=dt, stress=stress)

        final = self._run_results[-1] if self._run_results else {}
        survival = float(final.get("survival", 1.0))
        entropy = float(final.get("entropy", 0.5))

        bcl = BclNetwork(bcl_xl=self.bcl_xl)
        mito = MitochondriaModel(delta_psi_init=0.5 + survival * 0.45)
        mito.update(survival)
        casp = CaspaseCascade()
        casp.step(mito.cytochrome_c, dt=1.0)

        self._crep.update_from_state(
            network_coherence=bcl.network_coherence,
            membrane_resonance=mito.membrane_resonance,
            caspase_emergence=casp.emergence,
            atp_entropy=entropy,
        )

        elapsed = time.perf_counter() - t_start
        self._run_meta = {
            "n_cells": n_cells,
            "duration_hours": duration_hours,
            "stress": stress,
            "elapsed_s": round(elapsed, 4),
            "survival_final": survival,
            "phase_events_count": len(self._population.phase_events),
        }
        return {**self._run_meta, "crep": self._crep.as_dict()}

    def get_crep_state(self) -> dict[str, float]:
        """Return current CREP tensor {C, R, E, P, Gamma}."""
        return self._crep.as_dict()

    def get_utac_state(self) -> dict[str, object]:
        """Return UTAC state {H, dH_dt, H_star, K_eff}."""
        if self._run_results:
            last = self._run_results[-1]
            h = float(last.get("h", last.get("survival", 0.8)))
        else:
            h = 1.0
        H_star = ATP_THRESHOLD_MM / K_ATP
        gamma = self._crep.gamma
        h_star_crep = math.tanh(SIGMA_CREP * gamma)
        return {
            "H": h,
            "dH_dt": LOADING_RATE_R * (1.0 - h),
            "H_star": H_star,
            "H_star_crep": h_star_crep,
            "K_eff": K_ATP,
            "below_threshold": h < H_star,
        }

    def get_phase_events(self) -> list[dict[str, object]]:
        """Each apoptotic commitment = one phase event."""
        if self._population is None:
            return []
        return self._population.phase_events

    def to_zenodo_record(self) -> dict[str, object]:
        """Serialise full run to a Zenodo-compatible metadata record."""
        return {
            "title": "cellular-genesis: Apoptosis ATP Threshold UTAC Model (Package 25)",
            "description": (
                "UTAC simulation of programmed cell death. "
                "Models intracellular ATP dynamics, caspase cascade, and CREP criticality "
                f"(Γ ≈ {GAMMA_CELLULAR}) for a population of {self.n_cells} cells."
            ),
            "creators": [{"name": "Römer, Johann", "affiliation": "MOR Research Collective"}],
            "keywords": [
                "apoptosis", "ATP threshold", "UTAC", "CREP", "caspase", "mitochondria",
                "cellular criticality", "GenesisAeon", "Package 25",
            ],
            "related_identifiers": [
                {
                    "identifier": "10.3389/fcell.2025.1611055",
                    "relation": "isCitedBy",
                    "scheme": "doi",
                },
                {
                    "identifier": "10.5281/zenodo.19645351",
                    "relation": "isDocumentedBy",
                    "scheme": "doi",
                },
            ],
            "package_number": self.PACKAGE_NUMBER,
            "gamma": GAMMA_CELLULAR,
            "run_meta": self._run_meta,
            "crep_state": self._crep.as_dict(),
            "utac_state": self.get_utac_state(),
        }

    def survival_fraction(self, t: float) -> float:
        """Interpolate survival fraction at time t from run results."""
        if not self._run_results:
            return 1.0
        for r in reversed(self._run_results):
            if r["t"] <= t:
                return float(r["survival"])
        return float(self._run_results[0]["survival"])

    def trigger_computational_apoptosis(self, node_id: str) -> dict[str, object]:
        """Interface to genesis-os resource governance."""
        return self._governor.trigger_computational_apoptosis(node_id)
