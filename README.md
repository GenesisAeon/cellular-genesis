# cellular-genesis — Package 25

**Apoptosis / Programmed Cell Death ATP Threshold** — GenesisAeon Entropy Atlas Package 25

[![CI](https://github.com/GenesisAeon/diamond-setup/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/diamond-setup/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19645351.svg)](https://doi.org/10.5281/zenodo.19645351)
[![Package 25](https://img.shields.io/badge/GenesisAeon-Package%2025-purple)](https://github.com/GenesisAeon/diamond-setup)
[![Whitepaper](https://img.shields.io/badge/DOI-10.3389%2Ffcell.2025.1611055-orange)](https://doi.org/10.3389/fcell.2025.1611055)

Models intracellular ATP dynamics, mitochondrial membrane potential collapse, Bcl-2/Bcl-xL anti-apoptotic network coherence, and ultrasensitive caspase-3 activation for a stochastic cell population. Computes the CREP criticality index **Γ ≈ 0.090** for the apoptotic phase transition.

---

## Apoptosis UTAC Model

The system tracks the normalised ATP level **H(t) = [ATP] / K_ATP** with:

- **K** = 5.0 mM (healthy cytoplasmic ATP)
- **H\*** = 1.0 mM → η = H\*/K = **0.20** (cytochrome c release threshold)
- **Γ = arctanh(η) / σ ≈ 0.090** (cellular fragility / CREP criticality index, σ = 2.2)

When ATP falls below H\*, the mitochondrial membrane potential (Δψ) collapses, cytochrome c is released, and the ultrasensitive caspase-3 cascade (Hill coefficient n = 6) commits the cell to apoptosis irreversibly.

### CREP Tensor Components

| Symbol | Component | Description |
|--------|-----------|-------------|
| **C** | Coherence | Bcl-2/Bcl-xL anti-apoptotic network stability |
| **R** | Resonance | Mitochondrial membrane potential Δψ oscillation |
| **E** | Emergence | Caspase-3 ultrasensitive switch state |
| **P** | Population entropy | Cell-to-cell ATP variability (stochastic noise) |
| **Γ** | Criticality index | arctanh(η) / σ ≈ 0.090 |

---

## Install

```bash
pip install "diamond-setup[cellular]"
# or
uv add "diamond-setup[cellular]"
```

For the base package (no numpy/scipy):

```bash
pip install diamond-setup
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
├── __init__.py          # version, gamma, package number
├── constants.py         # ATP constants, CREP params, benchmark targets
├── atp_dynamics.py      # ODE model: dATP/dt
├── mitochondria.py      # Δψ collapse and cytochrome c release
├── bcl_network.py       # Bcl-2/Bcl-xL coherence network
├── caspase_cascade.py   # ultrasensitive Hill switch (n=6)
├── population.py        # stochastic N-cell population
├── crep_cellular.py     # CREP tensor {C, R, E, P, Γ}
├── resource_governor.py # genesis-os computational apoptosis bridge
├── system.py            # Diamond interface (run_cycle, get_crep_state, …)
└── benchmark.py         # literature benchmark suite
```

---

## BibTeX

```bibtex
@software{romer2025cellular_genesis,
  author    = {Römer, Johann},
  title     = {cellular-genesis: Apoptosis ATP Threshold UTAC Model — GenesisAeon Package 25},
  year      = {2025},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19645351},
  url       = {https://doi.org/10.5281/zenodo.19645351},
}

@article{fcell2025,
  doi     = {10.3389/fcell.2025.1611055},
  journal = {Frontiers in Cell and Developmental Biology},
  year    = {2025},
}
```

---

## diamond-setup CLI

This repo also hosts the **diamond-setup** scaffold tool — see [README_QUICKSTART.md](README_QUICKSTART.md).

```bash
diamond scaffold my-science-package --template genesis
```

Built with [uv](https://docs.astral.sh/uv/) · [Typer](https://typer.tiangolo.com/) · [Rich](https://rich.readthedocs.io/)
