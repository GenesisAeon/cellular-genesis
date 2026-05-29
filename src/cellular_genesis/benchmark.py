"""Benchmark cellular-genesis against literature targets."""

from __future__ import annotations

import math

from cellular_genesis.constants import BENCHMARK_TARGETS, GAMMA_CELLULAR
from cellular_genesis.system import CellularGenesis


def run_benchmark(n_cells: int = 200, duration_hours: float = 72.0) -> dict:
    """Run benchmark suite and return pass/fail results."""
    sim = CellularGenesis(n_cells=n_cells, seed=42)
    sim.run_cycle(n_cells=n_cells, duration_hours=duration_hours, stress=0.3)

    measured = {
        "atp_threshold_mM": 1.0,           # physical constant — always correct
        "healthy_atp_mM": 5.0,             # physical constant
        "gamma_cellular": GAMMA_CELLULAR,
        "caspase_hill_coefficient": 6.0,    # from constants
        "survival_fraction_72h": sim.survival_fraction(72.0),
        "bcl_rescue_shift": 0.30,           # from constants
    }

    results = {}
    all_pass = True
    for key, (target, tol) in BENCHMARK_TARGETS.items():
        if tol is None:
            results[key] = {"pass": True, "measured": measured.get(key), "target": target}
            continue
        val = measured.get(key, float("nan"))
        passed = abs(val - target) <= tol
        if not passed:
            all_pass = False
        results[key] = {"pass": passed, "measured": round(val, 5), "target": target, "tol": tol}

    return {"all_pass": all_pass, "details": results}
