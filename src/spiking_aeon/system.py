"""SpikingAeon — Diamond Interface for Package 26."""

from __future__ import annotations

import math
import time

from spiking_aeon.brian2_backend import Brian2Backend
from spiking_aeon.constants import (
    D_NOISE_OPTIMAL,
    DURATION_MS_DEFAULT,
    FIRING_RATE_CRITICAL_HZ,
    GAMMA_SNN,
    K_RATE,
    LOADING_RATE_R,
    LOIHI2_ACCURACY,
    LOIHI2_CORE_UTIL_PCT,
    LOIHI2_ENERGY_GOPS_W,
    LOIHI2_LATENCY_MS,
    N_NEURONS_DEFAULT,
    SIGMA_CREP,
)
from spiking_aeon.crep_snn import CREPSNN
from spiking_aeon.crep_to_weights import CREPtoWeightMapper
from spiking_aeon.loihi_adapter import LoihiAdapter
from spiking_aeon.stochastic_resonance import StochasticResonanceOptimizer


class SpikingAeon:
    """
    Diamond interface for Package 26 — Neuromorphic SNN Hardware Bridge.

    H(t)  = mean network firing rate / K_rate  (normalised, [0, 1])
    H*    = FIRING_RATE_CRITICAL_HZ / K_rate = 0.32
    Γ     ≈ 0.150  (SNN hardware criticality index)

    Mandatory Diamond contract:
      run_cycle, get_crep_state, get_utac_state, get_phase_events, to_zenodo_record
    """

    PACKAGE_NUMBER = 26
    DOMAIN = "neuromorphic-hardware"
    REFERENCE_DOI = "10.3389/fnins.2025.1676570"

    def __init__(
        self,
        n_neurons: int = N_NEURONS_DEFAULT,
        seed: int = 42,
    ) -> None:
        self.n_neurons = n_neurons
        self.seed = seed
        self._crep = CREPSNN()
        self._mapper = CREPtoWeightMapper()
        self._loihi = LoihiAdapter()
        self._sim_results: dict[str, float | int | list[dict[str, object]]] = {}
        self._phase_events: list[dict[str, object]] = []
        self._run_meta: dict[str, object] = {}

    # ── Diamond contract ────────────────────────────────────────────────────

    def run_cycle(
        self,
        duration_ms: float = DURATION_MS_DEFAULT,
        noise_amp: float = D_NOISE_OPTIMAL,
    ) -> dict[str, object]:
        """Run one SNN simulation cycle for `duration_ms` milliseconds."""
        t_start = time.perf_counter()

        lif_config = self._mapper.default_config()
        backend = Brian2Backend(
            n_neurons=self.n_neurons,
            weight_base=float(lif_config["weight_base"]),
            tau_m_ms=float(lif_config["tau_m_ms"]),
            i_noise_amp=noise_amp,
            tau_ref_ms=float(lif_config["tau_ref_ms"]),
            seed=self.seed,
        )
        self._sim_results = backend.run(duration_ms=duration_ms)
        raw_events = self._sim_results.get("phase_events", [])
        self._phase_events = list(raw_events) if isinstance(raw_events, list) else []

        spike_coherence = self._fget("spike_coherence", 0.5)
        mean_cv = self._fget("mean_isi_cv", 0.5)
        normalised_rate = self._fget("normalised_rate", 0.32)
        active_frac = self._fget("active_fraction", 0.8)

        # R: stochastic resonance proximity (low CV → high resonance)
        resonance_proximity = max(0.0, 1.0 - mean_cv)
        # E: accuracy proxy — how close normalised rate is to η_SNN target
        accuracy_vs_random = max(0.0, 1.0 - abs(normalised_rate - 0.32) / 0.32)
        # P: spike entropy proxy from active fraction
        spike_entropy = min(1.0, active_frac * 1.2)

        self._crep.update_from_simulation(
            spike_coherence=spike_coherence,
            resonance_proximity=resonance_proximity,
            accuracy_vs_random=accuracy_vs_random,
            spike_entropy=spike_entropy,
        )

        elapsed = time.perf_counter() - t_start
        self._run_meta = {
            "n_neurons": self.n_neurons,
            "duration_ms": duration_ms,
            "noise_amp": noise_amp,
            "elapsed_s": round(elapsed, 4),
            "mean_rate_hz": self._fget("mean_rate_hz", 0.0),
            "phase_events_count": len(self._phase_events),
            "backend": "brian2_synthetic",
            "loihi2_available": self._loihi.is_available,
        }
        return {**self._run_meta, "crep": self._crep.as_dict()}

    def get_crep_state(self) -> dict[str, float]:
        """Return current CREP tensor {C, R, E, P, Gamma}."""
        return self._crep.as_dict()

    def _fget(self, key: str, default: float) -> float:
        """Type-safe float extraction from _sim_results."""
        v = self._sim_results.get(key, default)
        return float(v) if isinstance(v, (int, float)) else default

    def get_utac_state(self) -> dict[str, object]:
        """Return UTAC state {H, dH_dt, H_star, K_eff}."""
        rate = self._fget("mean_rate_hz", FIRING_RATE_CRITICAL_HZ)
        h = rate / K_RATE
        h_star = FIRING_RATE_CRITICAL_HZ / K_RATE
        gamma = self._crep.gamma
        h_star_crep = math.tanh(SIGMA_CREP * gamma)
        return {
            "H": round(h, 4),
            "dH_dt": round(LOADING_RATE_R * (1.0 - h), 4),
            "H_star": h_star,
            "H_star_crep": round(h_star_crep, 4),
            "K_eff": K_RATE,
            "below_threshold": h < h_star,
        }

    def get_phase_events(self) -> list[dict[str, object]]:
        """Each network state transition = one phase event."""
        return self._phase_events

    def to_zenodo_record(self) -> dict[str, object]:
        """Serialise full run to a Zenodo-compatible metadata record."""
        return {
            "title": "spiking-aeon: Neuromorphic SNN Hardware Bridge UTAC Model (Package 26)",
            "description": (
                "UTAC simulation of a Spiking Neural Network on Intel Loihi 2. "
                "Maps CREP tensor components to LIF neuron parameters. "
                f"Γ ≈ {GAMMA_SNN} (SNN hardware criticality index, σ = 2.2). "
                f"Reference: NeuEdge (arXiv:2602.02439, 2026) — {LOIHI2_ENERGY_GOPS_W} GOp/s/W, "
                f"{LOIHI2_LATENCY_MS} ms latency, {LOIHI2_CORE_UTIL_PCT}% core utilisation."
            ),
            "creators": [{"name": "Römer, Johann", "affiliation": "MOR Research Collective"}],
            "keywords": [
                "spiking neural network", "neuromorphic", "Loihi 2", "CREP", "UTAC",
                "stochastic resonance", "LIF neuron", "GenesisAeon", "entropy atlas",
                "Package 26", "NeuEdge",
            ],
            "related_identifiers": [
                {
                    "identifier": "2602.02439",
                    "relation": "isCitedBy",
                    "scheme": "arxiv",
                },
                {
                    "identifier": "10.5281/zenodo.19645351",
                    "relation": "isDocumentedBy",
                    "scheme": "doi",
                },
            ],
            "package_number": self.PACKAGE_NUMBER,
            "gamma": GAMMA_SNN,
            "loihi2_benchmark": {
                "energy_GOp_s_W": LOIHI2_ENERGY_GOPS_W,
                "latency_ms": LOIHI2_LATENCY_MS,
                "core_util_pct": LOIHI2_CORE_UTIL_PCT,
                "accuracy": LOIHI2_ACCURACY,
            },
            "run_meta": self._run_meta,
            "crep_state": self._crep.as_dict(),
            "utac_state": self.get_utac_state(),
        }

    # ── Extended interface ──────────────────────────────────────────────────

    def deploy_to_loihi(self, crep_state: dict[str, float] | None = None) -> dict[str, object]:
        """Translate CREP → Loihi 2 configuration and deploy (requires INRC + Lava SDK)."""
        state = crep_state or self._crep.as_dict()
        lif_config = self._mapper.translate(state)
        return self._loihi.deploy(lif_config, n_neurons=self.n_neurons)

    def simulate_brian2(
        self,
        crep_state: dict[str, float] | None = None,
        duration_ms: float = DURATION_MS_DEFAULT,
    ) -> dict[str, float | int | list[dict[str, object]]]:
        """Software simulation fallback (no hardware needed)."""
        state = crep_state or self._crep.as_dict()
        lif_config = self._mapper.translate(state)
        backend = Brian2Backend(
            n_neurons=min(self.n_neurons, 200),
            weight_base=float(lif_config["weight_base"]),
            tau_m_ms=float(lif_config["tau_m_ms"]),
            i_noise_amp=float(lif_config["i_noise_amp"]),
            tau_ref_ms=float(lif_config["tau_ref_ms"]),
            seed=self.seed,
        )
        return backend.run(duration_ms=duration_ms)

    def optimise_stochastic_resonance(self, n_steps: int = 10) -> dict[str, object]:
        """Run stochastic resonance sweep and return optimal noise amplitude."""
        opt = StochasticResonanceOptimizer(
            n_neurons=min(self.n_neurons, 30),
            duration_ms=200.0,
            seed=self.seed,
        )
        return opt.sweep(n_steps=n_steps)
