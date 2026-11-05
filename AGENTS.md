# AGENTS.md — lensed-agn-detection (read FIRST, every session)

## Mission
Binary classifier: lensed AGN (label 1) vs contaminants (label 0) on 1-year LSST-like coadd
cutouts in 5 bands (g r i z y). Data is simulated: SLSim (fully synthetic, prefix D1) and
SIMCT (real HSC fields + injected objects, degraded, prefix D2). Challenge ends 2026-11-30 UTC.
Research question: "What makes a lensed-AGN classifier robust across simulation pipelines?"
(bands, pipeline transfer, ImageNet vs scratch, failure analysis).
The owner is a BEGINNER with astronomy data. Explain simply. Never guess anything marked
UNKNOWN in STATE.md: inspect the data or ask.

## Session start (always this order, nothing more)
1. Read STATE.md.
2. If the owner said "do phase N": read ONLY that section of docs/PHASES.md.
3. Read ONLY the skills/ files that section lists.
Do not scan the whole repo. Do not open data files in bulk.

## Commands the owner may type
- "do phase N"  -> run the Phase protocol below.
- "resume"      -> read STATE.md, continue from its "Next action".
- "review phase N" -> check that phase's checklist against the repo. No new features. Report pass/fail.
- "status"      -> summarize STATE.md in <= 8 lines.
- "explain X"   -> plain-language explanation. No code changes.

## Phase protocol
1. Do only that phase's tasks. No extras. Never start the next phase.
2. Smoke-test small first (skills/training-and-eval.md), then the real run.
3. Make the phase's required figures (skills/visualization.md) -> figures/, one line each in figures/INDEX.md.
4. Run the phase checklist. Fix failures.
5. Update STATE.md (overwrite sections) and append to DECISIONS.md (skills/state-and-decisions.md).
6. Commit + push (skills/git-checkpoint.md).
7. Reply in <= 10 lines: what was done / figures to look at (paths) / checklist pass-fail /
   what the owner should verify by eye / next phase.

## Token rules (strict)
- T1 Don't re-read files you just wrote or that haven't changed.
- T2 Use ls, head, grep -n, tail -n 20. Never cat big or binary files. Print <= 30 lines.
- T3 Debug on <= 200 objects. Smoke test = tiny subset, 1 epoch.
- T4 Edit with small patches, not whole-file rewrites.
- T5 Write each helper once in src/ and reuse it.
- T6 Send long logs to logs/*.txt and tail them.
- T7 No web browsing unless the owner asks.
- T8 Final reply <= 10 lines. No code dumps in chat; point to files.
- T9 No speculative refactors, no extra features, no README rewrites before Phase 10.
- T10 Ask at most ONE question, and only if blocked.

## Hard rules (mistakes we already decided to avoid)
- H1  Split by OBJECT, never by file. obj_key = f"{pipeline}_{cls}_{id}" (e.g. D1_L_00000042).
      All 5 bands of an object stay in the same split. Splits are created once, saved to
      splits/splits.csv (seeded) and reused. Never re-split silently.
- H2  Labels come only from the filename letter (N/L) or the label tables, and are used only as y.
      Never as an input feature. Test filenames carry only the band.
- H3  One data source per experiment (small OR main OR per-band). The small and per-band sets are
      SUBSETS of main (they overlap). Never train on one and validate on another.
      Record the source in STATE.md and results/runs.csv.
- H4  Normalize PER IMAGE (median/MAD + asinh). Any dataset-level statistic uses TRAIN split only.
- H5  Augment only with flips + 90-degree rotations, applied IDENTICALLY to all 5 bands of an
      object. No brightness/contrast/color jitter. No random crops. Colors are evidence.
- H6  The hidden test set is never used for training or tuning. Tune on val. The held-out split
      is touched once, at the end of a phase's final run.
- H7  Before trusting any score, run the shortcut checks (Phase 3). If a trivial model scores
      suspiciously high, STOP and report to the owner.
- H8  Report AUC, average precision, TPR@FPR=1e-2 and 1e-3, per pipeline (D1, D2) and overall.
      Never accuracy alone. Training is 50/50 but real validation will be lens-poor: choose
      thresholds on the realistic validation set. Do not resample val/test.
- H9  >= 3 seeds for any claim; report mean +/- std. A comparison changes exactly ONE thing
      (same data, splits, epochs, lr, augmentation).
- H10 Do not invent facts. Cutout size, FITS layout, label tables, official metric, submission
      format, test release: inspect or ask. Log what you verify in STATE.md.
- H11 Raw data is read-only. Data, zips, weights, caches never go in git. No hard-coded paths:
      use env var LENS_DATA_ROOT and configs/*.yaml.
- H12 Handle NaN/inf/sentinel values explicitly (count them, log them).
- H13 Shuffle training data. Check that IDs/file order don't encode the class.
- H14 Say "in these simulations", never "on real LSST data".
- H15 Decisions marked LOCKED in DECISIONS.md can't change without asking the owner.
- H16 Channel order is always g, r, i, z, y.

## Code style
Very commented, beginner-readable code. Follow skills/commenting-and-explaining.md.
Config-driven (YAML), seeded, functions <= 40 lines, helpers in src/.

## Visuals
Every phase produces its required figures. PNG, dpi 150, named phaseN_what.png.
The owner must be able to SEE lenses, failures and results. See skills/visualization.md.

## Git
Commit after every finished checklist item; push at every checkpoint and always at phase end.
Never push data or weights. See skills/git-checkpoint.md.

## Skills index (read only what the phase lists)
- skills/fits-and-data.md          reading FITS, filenames, manifest
- skills/leakage-guard.md          splits, leakage tests, shortcut checks
- skills/preprocessing-and-augmentation.md   normalization, augmentation
- skills/training-and-eval.md      models, training, metrics, smoke tests, runs.csv, Colab
- skills/visualization.md          figures to make and how
- skills/commenting-and-explaining.md        comment style for the owner
- skills/git-checkpoint.md         commit/push protocol
- skills/state-and-decisions.md    how to update STATE.md and DECISIONS.md
