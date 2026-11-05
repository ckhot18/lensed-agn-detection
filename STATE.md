# STATE.md — handoff file (agent: OVERWRITE sections, keep it short; <= 80 lines)
Any agent must be able to continue from this file alone.

Last updated: 2026-11-05, Codex
Last commit: HEAD (phase-2 checkpoint pending)

## Now
Current phase: 2
Status: complete
Next action: do phase 3

## Phase tracker
| Phase | Name                              | Status      |
|-------|-----------------------------------|-------------|
| 0     | Scaffold + environment            | complete    |
| 1     | Data inspection                   | complete    |
| 2     | Dataset, splits, leakage tests    | complete    |
| 3     | Baselines + shortcut checks       | not started |
| 4     | Small CNN baseline                | not started |
| 5     | ResNet-18 scratch vs pretrained   | not started |
| 6     | Experiment A: bands               | not started |
| 7     | Experiment B: pipeline transfer   | not started |
| 8     | Failure analysis + prior shift    | not started |
| 9     | Test predictions + submission     | not started |
| 10    | Write-up + polish                 | not started |

## Verified facts (fill ONLY after inspecting; otherwise leave UNKNOWN)
- Cutout size (H x W): 41 x 41 (inspected D1 lens, D1 non-lens, D2 lens)
- FITS layout (image in primary HDU? table column?): one 2-D image in the primary HDU; no extensions in inspected files
- dtype / units: FITS big-endian float64; units are not recorded in inspected headers
- Objects per simset, total: small source = 4,000 objects / 20,000 files (1,000 each D1_L, D1_N, D2_L, D2_N). Guide confirms 4,000 small; main 50k x 4 would be 200k, so the separate “100k training images” claim is unverified here.
- Label tables: no truth/label table is supplied in raw small data or project metadata; filename L/N is the only label. Doubles/quads and contaminant types are not available.
- Official lens-poor validation set: when released, it is EVAL-ONLY; never train or tune on it.
- Official metric: UNKNOWN
- Submission format: UNKNOWN
- Test set released? UNKNOWN (site said "generated soon")
- Realistic validation set released? UNKNOWN

## Environment
- Data source in use (small | main | per-band): small
- LENS_DATA_ROOT: D:\\Research\\lensed-agn-detection\\data\\raw (exists; 20,000 FITS files)
- Python / torch / GPU: Python 3.12.10; torch 2.15.0+cpu; CUDA unavailable; astropy 8.0.2; sklearn 1.9.1
- Commands that work: `$env:LENS_DATA_ROOT=(Join-Path (Get-Location) 'data/raw'); .\\.venv\\Scripts\\python.exe src/check_env.py`; `.\\.venv\\Scripts\\python.exe -m pytest`; `.\\.venv\\Scripts\\python.exe src/splits.py --config configs/splits.yaml`; `.\\.venv\\Scripts\\python.exe -m src.phase2_figures`

## Open issues / blockers
- Main-data count discrepancy remains unverified from the supplied small dataset or metadata.
