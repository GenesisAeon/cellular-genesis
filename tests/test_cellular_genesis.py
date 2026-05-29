"""Tests for cellular-genesis Package 25."""

import math

from cellular_genesis.atp_dynamics import ATPDynamicsModel
from cellular_genesis.caspase_cascade import CaspaseCascade
from cellular_genesis.constants import ATP_THRESHOLD_MM, GAMMA_CELLULAR, K_ATP
from cellular_genesis.crep_cellular import CREPCellular
from cellular_genesis.system import CellularGenesis


def test_atp_threshold():
    assert abs(ATP_THRESHOLD_MM - 1.0) < 1e-6
    assert abs(K_ATP - 5.0) < 1e-6


def test_gamma_reference():
    eta = ATP_THRESHOLD_MM / K_ATP  # 0.20
    gamma_expected = math.atanh(eta) / 2.2
    assert abs(GAMMA_CELLULAR - gamma_expected) < 0.005


def test_atp_dynamics_runs():
    model = ATPDynamicsModel(seed=42)
    history = model.run(duration_hours=10.0, dt=0.5)
    assert len(history) > 0
    assert all(0.0 <= r["atp"] <= 5.0 for r in history)


def test_caspase_ultrasensitivity():
    casp = CaspaseCascade()
    # Low cytochrome c → stays near zero
    for _ in range(50):
        casp.step(cytochrome_c=0.05)
    assert casp.caspase < 0.1
    # High cytochrome c → switches on
    for _ in range(100):
        casp.step(cytochrome_c=0.9)
    assert casp.caspase > 0.5
    assert casp.committed


def test_crep_gamma_range():
    crep = CREPCellular(C=0.6, R=0.5, E=0.1, P=0.7)
    assert 0.0 < crep.gamma < 1.0
    assert abs(crep.gamma_reference - GAMMA_CELLULAR) < 1e-6


def test_diamond_interface():
    sim = CellularGenesis(n_cells=50, seed=42)
    result = sim.run_cycle(n_cells=50, duration_hours=12.0, stress=0.0, dt=1.0)
    assert "survival_final" in result
    assert 0.0 <= result["survival_final"] <= 1.0

    crep = sim.get_crep_state()
    assert {"C", "R", "E", "P", "Gamma"} <= crep.keys()

    utac = sim.get_utac_state()
    assert {"H", "H_star", "K_eff"} <= utac.keys()

    events = sim.get_phase_events()
    assert isinstance(events, list)

    record = sim.to_zenodo_record()
    assert record["package_number"] == 25
    assert abs(record["gamma"] - GAMMA_CELLULAR) < 1e-6
