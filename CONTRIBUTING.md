# Contributing

This is a research repository. Correct comparisons and reproducibility matter more than feature speed.

## Before opening a change

1. Read `AGENTS.md` and `STATE.md`.
2. Keep raw data, model weights, caches, and notebook checkpoints out of Git.
3. Use `LENS_DATA_ROOT`; do not add machine-specific data paths.
4. Add a focused test when changing loading, splitting, normalization, or augmentation.
5. Run the checks below before committing.

```powershell
.\.venv\Scripts\python.exe -m pytest
git diff --check
```

## Research safeguards

- Preserve channel order: `g, r, i, z, y`.
- Keep all bands from one object in the same split.
- Never use labels as input features.
- Apply one shared spatial augmentation to all five bands.
- Do not tune on the holdout set.
- Record experiments, seed, data source, and commit in `results/runs.csv`.

## Commit style

Use concise, phase-scoped messages such as `phase3: add summary-stat baseline`. Do not force-push or rewrite research history.
