# Release Guide

This package follows the GenesisAeon ecosystem release process.

## Versioning

We use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

- **MAJOR** — breaking changes to the public API or Diamond Interface
  (`run_cycle`, `get_crep_state`, `get_utac_state`, `get_phase_events`,
  `to_zenodo_record`) of `CellularGenesis` or `SpikingAeon`.
- **MINOR** — new features, backwards-compatible.
- **PATCH** — bug fixes, documentation, dependency bumps.

## How to cut a release

1. Ensure `CHANGELOG.md` has an entry for the new version under
   `## [X.Y.Z]`.
2. Ensure `pyproject.toml`'s `[project].version`, `.zenodo.json`'s
   `"version"`, and the `__version__` strings in
   `src/cellular_genesis/__init__.py` and `src/spiking_aeon/__init__.py`
   all match.
3. Commit these changes to `main`.
4. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
5. The `.github/workflows/release.yml` workflow builds, publishes to
   PyPI, creates a GitHub Release, and triggers the Zenodo upload job.

## Dependency pins within the GenesisAeon ecosystem

If this package depends on other `GenesisAeon/*` packages, pin them with
`>=` lower bounds matching the minimum version that provides the API this
package relies on. Do not pin exact versions (`==`) for ecosystem
dependencies.
