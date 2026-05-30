# cellular-genesis — Package 25

**Apoptosis / Programmed Cell Death ATP Threshold** — GenesisAeon Entropy Atlas Package 25

[![CI](https://github.com/GenesisAeon/cellular-genesis/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/cellular-genesis/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19645351.svg)](https://doi.org/10.5281/zenodo.19645351)
[![Package 25](https://img.shields.io/badge/GenesisAeon-Package%2025-purple)](https://github.com/GenesisAeon/cellular-genesis)
[![Whitepaper](https://img.shields.io/badge/DOI-10.3389%2Ffcell.2025.1611055-orange)](https://doi.org/10.3389/fcell.2025.1611055)

Models intracellular ATP dynamics, mitochondrial membrane potential collapse,
Bcl-2/Bcl-xL anti-apoptotic network coherence, and ultrasensitive caspase-3
activation for a stochastic cell population. Computes the CREP criticality
index **Gamma ~= 0.090** for the apoptotic phase transition.

---

## Apoptosis UTAC Model

| Parameter | Value | Meaning |
|-----------|-------|---------|
| **K** | 5.0 mM | Healthy cytoplasmic ATP ceiling |
| **H*** | 1.0 mM | Cytochrome c release threshold |
| **eta** | 0.20 | H*/K — cellular fragility setpoint |
| **Gamma** | ~0.090 | arctanh(0.20) / 2.2 — CREP criticality index |

When ATP falls below H*, the mitochondrial membrane potential (delta-psi)
collapses, cytochrome c is released, and the ultrasensitive caspase-3 cascade
(Hill coefficient n = 6) commits the cell to apoptosis irreversibly.

### CREP Tensor Components

| Symbol | Component | Description |
|--------|-----------|-------------|
| **C** | Coherence | Bcl-2/Bcl-xL anti-apoptotic network stability |
| **R** | Resonance | Mitochondrial membrane potential oscillation |
| **E** | Emergence | Caspase-3 ultrasensitive switch state |
| **P** | Population entropy | Cell-to-cell ATP variability (stochastic noise) |
| **Gamma** | Criticality index | arctanh(eta) / sigma ~= 0.090 |

---

## Install

```bash
pip install "cellular-genesis[cellular]"
# or
uv add "cellular-genesis[cellular]"
```

---

## Usage

```python
from cellular_genesis.system import CellularGenesis

sim = CellularGenesis(n_cells=1000, bcl_xl=0.5, seed=42)

# Run 48 h simulation under mild stress
result = sim.run_cycle(duration_hours=48.0, stress=0.1)
print(f"Survival fraction: {result['survival_final']:.3f}")
print(f"Phase events (apoptoses): {result['phase_events_count']}")

# CREP criticality tensor
crep = sim.get_crep_state()
print(f"Gamma = {crep['Gamma']:.4f}  (reference: {crep['Gamma_ref']})")

# UTAC state
utac = sim.get_utac_state()
print(f"H = {utac['H']:.3f}, H* = {utac['H_star']}, below threshold: {utac['below_threshold']}")

# Zenodo record
record = sim.to_zenodo_record()
```

### Benchmark

```python
from cellular_genesis.benchmark import run_benchmark
results = run_benchmark(n_cells=200, duration_hours=72.0)
print(results["all_pass"])   # True if all targets met
```

---

## Package Structure

```
src/cellular_genesis/
├── __init__.py          # version 0.1.1, gamma=0.090, package_number=25
├── constants.py         # ATP constants, CREP params, benchmark targets
├── atp_dynamics.py      # ODE model: dATP/dt
├── mitochondria.py      # delta-psi collapse and cytochrome c release
├── bcl_network.py       # Bcl-2/Bcl-xL coherence network
├── caspase_cascade.py   # ultrasensitive Hill switch (n=6)
├── population.py        # stochastic N-cell population
├── crep_cellular.py     # CREP tensor {C, R, E, P, Gamma}
├── resource_governor.py # genesis-os computational apoptosis bridge
├── system.py            # Diamond interface (run_cycle, get_crep_state, ...)
└── benchmark.py         # literature benchmark suite
```

---

## CREP Criticality Spectrum Position

```
Domain                       Pkg   Gamma    eta
---------------------------  ----  -------  ----
Qubit decoherence (T2)       P24   0.050    ~5%
Apoptosis (ATP threshold)    P25   0.090    20%   <- cellular-genesis
Amazon Rainforest            P19   0.116    12%
SNN firing (Loihi 2)         P26   0.150    32%
Seismic b=1.5 (GR law)       P23   0.200    40%
AMOC / Neural criticality    P20   0.251    50%
```

---

## BibTeX

```bibtex
@software{romer2025cellular_genesis,
  author    = {Romer, Johann},
  title     = {cellular-genesis: Apoptosis ATP Threshold UTAC Model (Package 25)},
  year      = {2025},
  version   = {0.1.1},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19645351},
}

@article{fcell2025,
  doi     = {10.3389/fcell.2025.1611055},
  journal = {Frontiers in Cell and Developmental Biology},
  year    = {2025},
}
```
