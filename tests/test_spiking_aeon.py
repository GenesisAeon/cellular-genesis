"""Tests for spiking-aeon Package 26."""

from __future__ import annotations

import math

import pytest

from spiking_aeon.benchmark import run_benchmark
from spiking_aeon.constants import ETA_SNN, GAMMA_SNN
from spiking_aeon.crep_snn import CREPSNN
from spiking_aeon.crep_to_weights import CREPtoWeightMapper
from spiking_aeon.lif_neuron import LIFNeuron
from spiking_aeon.loihi_adapter import LoihiAdapter
from spiking_aeon.stdp_plasticity import STDPRule
from spiking_aeon.system import SpikingAeon

# ── LIF neuron ──────────────────────────────────────────────────────────────

def test_lif_fires_under_strong_input() -> None:
    neu = LIFNeuron()
    fired = False
    for step in range(2000):
        if neu.step(t=step * 0.1, i_syn=2.0, i_noise=0.0, dt=0.1):
            fired = True
            break
    assert fired, "LIF neuron should fire under strong synaptic drive"


def test_lif_silent_without_input() -> None:
    neu = LIFNeuron()
    for step in range(200):
        neu.step(t=step * 0.1, i_syn=0.0, i_noise=0.0, dt=0.1)
    assert len(neu.spike_times) == 0, "LIF should not fire without input"


def test_lif_crep_modulation_raises_threshold_toward_zero() -> None:
    neu = LIFNeuron()
    original = neu.v_threshold
    neu.apply_crep(gamma=0.5)
    # Threshold moves closer to 0 (less negative) → easier to fire
    assert neu.v_threshold > original


# ── STDP ────────────────────────────────────────────────────────────────────

def test_stdp_potentiation() -> None:
    rule = STDPRule()
    dw = rule.dw(delta_t_ms=5.0)
    assert dw > 0


def test_stdp_depression() -> None:
    rule = STDPRule()
    dw = rule.dw(delta_t_ms=-5.0)
    assert dw < 0


def test_stdp_weight_clipping() -> None:
    rule = STDPRule()
    w = rule.update_weight(0.99, delta_t_ms=1.0)
    assert w <= 1.0
    w = rule.update_weight(0.01, delta_t_ms=-1.0)
    assert w >= 0.0


# ── CREP tensor ─────────────────────────────────────────────────────────────

def test_crep_gamma_reference() -> None:
    crep = CREPSNN()
    assert abs(crep.gamma_reference - GAMMA_SNN) < 1e-6


def test_crep_eta() -> None:
    assert abs(ETA_SNN - 0.32) < 1e-6


def test_crep_gamma_formula() -> None:
    expected = math.atanh(0.32) / 2.2
    assert abs(GAMMA_SNN - expected) < 0.005


def test_crep_update() -> None:
    crep = CREPSNN()
    crep.update_from_simulation(0.4, 0.5, 0.6, 0.7)
    assert crep.C == 0.4
    assert crep.R == 0.5
    assert crep.E == 0.6
    assert crep.P == 0.7


def test_crep_as_dict_keys() -> None:
    crep = CREPSNN()
    d = crep.as_dict()
    for key in ("C", "R", "E", "P", "Gamma", "Gamma_ref", "eta"):
        assert key in d


# ── CREPtoWeightMapper ───────────────────────────────────────────────────────

def test_mapper_translate() -> None:
    mapper = CREPtoWeightMapper()
    config = mapper.translate({"C": 0.5, "R": 0.5, "E": 0.5, "P": 0.5, "Gamma": 0.15})
    assert "tau_m_ms" in config
    assert "i_noise_amp" in config
    assert "weight_base" in config
    assert "tau_ref_ms" in config


def test_mapper_default_config() -> None:
    mapper = CREPtoWeightMapper()
    config = mapper.default_config()
    assert config["gamma_applied"] == 0.150


# ── SpikingAeon diamond interface ───────────────────────────────────────────

@pytest.fixture
def sim() -> SpikingAeon:
    return SpikingAeon(n_neurons=50, seed=42)


def test_run_cycle_returns_dict(sim: SpikingAeon) -> None:
    result = sim.run_cycle(duration_ms=100.0)
    assert isinstance(result, dict)
    assert "crep" in result
    assert "mean_rate_hz" in result


def test_get_crep_state(sim: SpikingAeon) -> None:
    sim.run_cycle(duration_ms=100.0)
    crep = sim.get_crep_state()
    for key in ("C", "R", "E", "P", "Gamma"):
        assert key in crep


def test_get_utac_state(sim: SpikingAeon) -> None:
    sim.run_cycle(duration_ms=100.0)
    utac = sim.get_utac_state()
    for key in ("H", "dH_dt", "H_star", "K_eff", "below_threshold"):
        assert key in utac
    assert utac["K_eff"] == 1000.0
    assert isinstance(utac["below_threshold"], bool)


def test_get_phase_events(sim: SpikingAeon) -> None:
    sim.run_cycle(duration_ms=100.0)
    events = sim.get_phase_events()
    assert isinstance(events, list)


def test_to_zenodo_record(sim: SpikingAeon) -> None:
    sim.run_cycle(duration_ms=100.0)
    record = sim.to_zenodo_record()
    assert record["package_number"] == 26
    assert record["gamma"] == GAMMA_SNN
    assert "loihi2_benchmark" in record
    assert "crep_state" in record
    assert "utac_state" in record


def test_simulate_brian2(sim: SpikingAeon) -> None:
    result = sim.simulate_brian2(duration_ms=100.0)
    assert "mean_rate_hz" in result


# ── Loihi adapter ───────────────────────────────────────────────────────────

def test_loihi_deploy_raises_without_lava() -> None:
    adapter = LoihiAdapter()
    if not adapter.is_available:
        with pytest.raises(RuntimeError, match="Lava SDK not installed"):
            adapter.deploy({})


# ── Benchmark ───────────────────────────────────────────────────────────────

def test_benchmark_all_pass() -> None:
    result = run_benchmark(n_neurons=50, duration_ms=200.0)
    assert result["all_pass"] is True, f"Benchmark failed: {result['details']}"
