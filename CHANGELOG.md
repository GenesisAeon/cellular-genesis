# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
- This repository publishes under the PyPI name `diamond-setup` and bundles
  three packages (`diamond_setup`, `cellular_genesis` — Package 25, and
  `spiking_aeon` — Package 26). The GenesisAeon ecosystem registry lists
  `cellular-genesis` (P25) as a standalone entry; see the release PR
  description for details on this naming discrepancy.
