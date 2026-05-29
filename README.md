# GenesisAeon Entropy Atlas — Packages 25 & 26

**Package 25: Apoptosis / Programmed Cell Death ATP Threshold**
**Package 26: Neuromorphic SNN Hardware Bridge (Intel Loihi 2)**

[![CI](https://github.com/GenesisAeon/diamond-setup/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/diamond-setup/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19645351.svg)](https://doi.org/10.5281/zenodo.19645351)
[![Package 25](https://img.shields.io/badge/GenesisAeon-Package%2025-purple)](https://github.com/GenesisAeon/diamond-setup)
[![Package 26](https://img.shields.io/badge/GenesisAeon-Package%2026-blueviolet)](https://github.com/GenesisAeon/diamond-setup)
[![Whitepaper](https://img.shields.io/badge/DOI-10.3389%2Ffcell.2025.1611055-orange)](https://doi.org/10.3389/fcell.2025.1611055)
[![NeuEdge](https://img.shields.io/badge/arXiv-2602.02439-red)](https://arxiv.org/abs/2602.02439)

---

## Package 25 — cellular-genesis: Apoptosis ATP Threshold

Models intracellular ATP dynamics, mitochondrial membrane potential collapse, Bcl-2/Bcl-xL anti-apoptotic network coherence, and ultrasensitive caspase-3 activation for a stochastic cell population. Computes the CREP criticality index **Γ ≈ 0.090** for the apoptotic phase transition.

### Apoptosis UTAC Model

| Parameter | Value | Meaning |
|-----------|-------|---------|
| **K** | 5.0 mM | Healthy cytoplasmic ATP ceiling |
| **H\*** | 1.0 mM | Cytochrome c release threshold |
| **η** | 0.20 | H\*/K — cellular fragility setpoint |
| **Γ** | ≈ 0.090 | arctanh(0.20) / 2.2 — CREP criticality index |

### CREP Tensor (P25)

| Symbol | Component | Description |
|--------|-----------|-------------|
| **C** | Coherence | Bcl-2/Bcl-xL anti-apoptotic network stability |
| **R** | Resonance | Mitochondrial membrane potential Δψ oscillation |
| **E** | Emergence | Caspase-3 ultrasensitive switch state |
| **P** | Population entropy | Cell-to-cell ATP variability (stochastic noise) |
| **Γ** | Criticality index | arctanh(η) / σ ≈ 0.090 |

### Usage

```python
from cellular_genesis.system import CellularGenesis

sim = CellularGenesis(n_cells=1000, bcl_xl=0.5, seed=42)
result = sim.run_cycle(duration_hours=48.0, stress=0.1)
print(f"Survival fraction: {result['survival_final']:.3f}")

crep = sim.get_crep_state()
print(f"Gamma = {crep['Gamma']:.4f}  (reference: {crep['Gamma_ref']})")

utac = sim.get_utac_state()
record = sim.to_zenodo_record()
```

---

## Package 26 — spiking-aeon: Neuromorphic SNN Hardware Bridge

Bridges the GenesisAeon CREP weight system to physical Spiking Neural Network hardware (Intel Loihi 2). CREP tensor components C, R, E, P are translated into LIF neuron parameters (membrane time constants, synaptic weights, noise amplitudes, refractory periods). Software simulation runs without hardware via the Brian2-compatible pure-Python backend.

Calibrated against **NeuEdge (arXiv:2602.02439, 2026)**: 847 GOp/s/W · 2.3 ms latency · 89% core utilisation · 312× energy improvement over GPU.

### SNN UTAC Model

| Parameter | Value | Meaning |
|-----------|-------|---------|
| **K** | 1000 Hz | Max sustainable Loihi 2 firing rate |
| **H\*** | 320 Hz | Critical firing rate for task performance |
| **η** | 0.32 | H\*/K — SNN operating setpoint |
| **Γ** | ≈ 0.150 | arctanh(0.32) / 2.2 — SNN hardware criticality index |

### CREP → LIF Parameter Mapping (P26)

| CREP | LIF Parameter | High value effect |
|------|---------------|-------------------|
| **C** | τ_m (membrane time constant) | Longer integration window |
| **R** | I_noise amplitude | Optimal stochastic resonance |
| **E** | Synaptic weight W | Stronger collective coupling |
| **P** | τ_ref (refractory period) | Richer temporal coding |

### Usage

```python
from spiking_aeon.system import SpikingAeon

sim = SpikingAeon(n_neurons=1000, seed=42)

# Software simulation (no hardware required)
result = sim.run_cycle(duration_ms=1000.0)
print(f"Mean firing rate: {result['mean_rate_hz']:.1f} Hz")

crep = sim.get_crep_state()
print(f"Gamma = {crep['Gamma']:.4f}  (reference: {crep['Gamma_ref']})")

utac = sim.get_utac_state()
print(f"H = {utac['H']:.4f}, H* = {utac['H_star']}, below threshold: {utac['below_threshold']}")

# Zenodo record with full Loihi 2 benchmark metadata
record = sim.to_zenodo_record()

# Deploy to Loihi 2 (requires INRC access + pip install lava-nc)
# sim.deploy_to_loihi()
```

### Stochastic Resonance

```python
sr = sim.optimise_stochastic_resonance(n_steps=20)
print(f"Optimal noise D_res = {sr['D_res']:.3f}  (min CV = {sr['min_CV']:.3f})")
```

---

## Install

```bash
# Package 25 (apoptosis) — includes numpy/scipy
pip install "diamond-setup[cellular]"

# Package 26 (SNN) — includes numpy
pip install "diamond-setup[spiking]"

# Both packages
pip install "diamond-setup[cellular,spiking]"

# Base (no scientific dependencies)
pip install diamond-setup
```

---

## CREP Criticality Spectrum Position

```
Domain                       Pkg   Γ_domain   η_setpoint
───────────────────────────  ────  ─────────  ───────────
Qubit decoherence (T2)       P24   0.050      ~5%
Apoptosis (ATP threshold)    P25   0.090      20%        ← cellular-genesis
Amazon Rainforest            P19   0.116      12%
SNN firing (Loihi 2)         P26   0.150      32%        ← spiking-aeon
Seismic b=1.5 (GR law)       P23   0.200      ~40%
AMOC / Neural criticality    P18/20 0.251     50%        ← triple universality
BTW Sandpile (SOC)           P22   0.296      58%
```

---

## Package Structure

```
src/
├── cellular_genesis/        # Package 25 — Apoptosis
│   ├── __init__.py          # version 0.2.0, gamma=0.090, package_number=25
│   ├── constants.py
│   ├── atp_dynamics.py
│   ├── mitochondria.py
│   ├── bcl_network.py
│   ├── caspase_cascade.py
│   ├── population.py
│   ├── crep_cellular.py
│   ├── resource_governor.py
│   ├── system.py            # Diamond interface
│   └── benchmark.py
└── spiking_aeon/            # Package 26 — Neuromorphic SNN
    ├── __init__.py          # version 0.2.0, gamma=0.150, package_number=26
    ├── constants.py
    ├── lif_neuron.py        # LIF neuron (CREP-modulated threshold)
    ├── stdp_plasticity.py   # Spike-Timing Dependent Plasticity
    ├── stochastic_resonance.py  # Optimal noise sweep (Ferreira 2025)
    ├── crep_to_weights.py   # CREP tensor → LIF network parameters
    ├── crep_snn.py          # SNN CREP tensor {C, R, E, P, Γ}
    ├── brian2_backend.py    # Pure-Python LIF network simulation
    ├── loihi_adapter.py     # Loihi 2 / Lava SDK interface stub
    ├── system.py            # Diamond interface
    └── benchmark.py
```

---

## BibTeX

```bibtex
@software{romer2026genesis_atlas,
  author    = {Römer, Johann},
  title     = {GenesisAeon Entropy Atlas — Packages 25 \& 26},
  year      = {2026},
  version   = {0.2.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19645351},
  url       = {https://doi.org/10.5281/zenodo.19645351},
}

@article{fcell2025,
  doi     = {10.3389/fcell.2025.1611055},
  journal = {Frontiers in Cell and Developmental Biology},
  year    = {2025},
  note    = {Package 25 reference},
}

@misc{neuredge2026,
  title  = {NeuEdge: Energy-Efficient Neuromorphic Edge Computing},
  year   = {2026},
  eprint = {2602.02439},
  note   = {Package 26 reference — 847 GOp/s/W on Loihi 2},
}
```

---

## diamond-setup CLI

This repo also hosts the **diamond-setup** scaffold tool — see [README_QUICKSTART.md](README_QUICKSTART.md).

```bash
diamond scaffold my-science-package --template genesis
```

Built with [uv](https://docs.astral.sh/uv/) · [Typer](https://typer.tiangolo.com/) · [Rich](https://rich.readthedocs.io/)
