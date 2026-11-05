# STATE.md — handoff file (agent: OVERWRITE sections, keep it short; <= 80 lines)
Any agent must be able to continue from this file alone.

Last updated: 2026-11-05, Codex
Last commit: HEAD (phase-0 checkpoint)

## Now
Current phase: 0
Status: complete
Next action: do phase 1

## Phase tracker
| Phase | Name                              | Status      |
|-------|-----------------------------------|-------------|
| 0     | Scaffold + environment            | complete    |
| 1     | Data inspection                   | not started |
| 2     | Dataset, splits, leakage tests    | not started |
| 3     | Baselines + shortcut checks       | not started |
| 4     | Small CNN baseline                | not started |
| 5     | ResNet-18 scratch vs pretrained   | not started |
| 6     | Experiment A: bands               | not started |
| 7     | Experiment B: pipeline transfer   | not started |
| 8     | Failure analysis + prior shift    | not started |
| 9     | Test predictions + submission     | not started |
| 10    | Write-up + polish                 | not started |

## Verified facts (fill ONLY after inspecting; otherwise leave UNKNOWN)
- Cutout size (H x W): UNKNOWN
- FITS layout (image in primary HDU? table column?): UNKNOWN
- dtype / units: UNKNOWN
- Objects per simset, total: UNKNOWN (note says 100k training images but also 50k x 4 simsets: resolve)
- Label tables: columns, doubles/quads flag, contaminant type: UNKNOWN
- Official metric: UNKNOWN
- Submission format: UNKNOWN
- Test set released? UNKNOWN (site said "generated soon")
- Realistic validation set released? UNKNOWN

## Environment
- Data source in use (small | main | per-band): small
- LENS_DATA_ROOT: D:\\Research\\lensed-agn-detection\\data\\raw (exists; 20,000 FITS files)
- Python / torch / GPU: Python 3.12.10; torch 2.15.0+cpu; CUDA unavailable; astropy 8.0.2; sklearn 1.9.1
- Commands that work: `$env:LENS_DATA_ROOT=(Join-Path (Get-Location) 'data/raw'); .\\.venv\\Scripts\\python.exe src/check_env.py`; `.\\.venv\\Scripts\\python.exe -m pytest`

## Open issues / blockers
- none
