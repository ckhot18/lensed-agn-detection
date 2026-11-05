# Lensed AGN Detection

Reproducible research code for classifying simulated five-band LSST-like cutouts as **lensed AGN** or **non-lens contaminants**.

> Scope: results from this repository apply to these simulations, not directly to real LSST data.

## Current status

Phases 0–2 are complete: the small dataset is inspected, a 5-band object loader is available, and a fixed object-level split is saved. Model baselines begin in Phase 3.

| Item | Current value |
| --- | --- |
| Input | Five aligned bands in order `g, r, i, z, y` |
| Small dataset | 4,000 objects / 20,000 FITS files |
| Cutouts | 41 x 41 primary-HDU FITS images |
| Split | Seeded 70/15/15 train/validation/holdout, stratified by pipeline and class |
| Normalization | Per-image median/MAD followed by `asinh` |
| Augmentation | Shared 90° rotations and left/right flips for training only |

## Quick start

Use Python 3.12 and place the unzipped small dataset under `data/raw/`. Raw data, weights, and caches are intentionally ignored by Git.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:LENS_DATA_ROOT = (Join-Path (Get-Location) 'data/raw')
.\.venv\Scripts\python.exe src/check_env.py
.\.venv\Scripts\python.exe -m pytest
```

Create or validate the fixed split and regenerate Phase 2 figures:

```powershell
.\.venv\Scripts\python.exe src/splits.py --config configs/splits.yaml
.\.venv\Scripts\python.exe -m src.phase2_figures
```

## Reproducibility rules

- Split by object, never by individual FITS file; the five bands always stay together.
- Reuse [`splits/splits.csv`](splits/splits.csv). Do not silently re-split.
- Labels come only from the filename class letter and are never image features.
- Use one data source per experiment; do not mix small and main data in an experiment.
- Keep the holdout set untouched until the final run of a phase.
- Set seeds in configs and record each run in `results/runs.csv`.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/data.py` | FITS loading, normalization, labels, and deterministic D4 augmentation |
| `src/splits.py` | Reproducible object-level split creation and reuse |
| `configs/splits.yaml` | Versioned split recipe |
| `tests/` | Fast data, split, and leakage tests |
| `figures/` | Phase figures with descriptions in `figures/INDEX.md` |
| `STATE.md` | Current project handoff and verified facts |
| `DECISIONS.md` | Append-only research decisions |

## Data and limitations

The supplied small data contains filename labels (`L` or `N`) but no truth table for lens multiplicity or contaminant type. The official metric, submission format, and released test/realistic-validation status remain unverified. See [`STATE.md`](STATE.md) for the current evidence.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Before changing research behavior, read [`AGENTS.md`](AGENTS.md): it contains the project’s leakage, normalization, and evaluation safeguards.
