# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Changed
- PyPI distribution name changed from `diamond-setup` to `cellular-genesis`
  to match the GitHub repository name and the GenesisAeon ecosystem
  registry entry for Package 25. The bundled `diamond_setup` scaffold
  tool keeps its own module/CLI name (`diamond` command,
  `src/diamond_setup`); only the top-level package name that `pip`
  resolves has changed.

## [1.0.0] - 2026
### Added
- Initial v1.0.0 release as part of the GenesisAeon ecosystem-wide 1.0.0
  milestone.
- Standardized release tooling: `RELEASE_GUIDE.md`, `CONTRIBUTING.md`,
  issue/PR templates.

### Changed
- Project metadata (`pyproject.toml`, `.zenodo.json`, package `__version__`
  strings for `cellular_genesis` and `spiking_aeon`) bumped from 0.2.0 to
  1.0.0.

### Note
- At the time of this release, this repository published under the PyPI
  name `diamond-setup` and bundled three packages (`diamond_setup`,
  `cellular_genesis` — Package 25, and `spiking_aeon` — Package 26). The
  PyPI name was subsequently changed to `cellular-genesis` — see the
  `[Unreleased]` entry above.
