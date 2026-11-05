# PHASES.md — read ONLY the section the owner names
Owner types: "do phase N". Optional richer prompt shown at each phase.
After every phase: figures made, checklist run, STATE.md + DECISIONS.md updated, commit + push.
Phases 0-4 use the SMALL dataset. Phase 5 starts with a scale-up to MAIN (or a fixed subset of it); Phases 5-8 all stay on MAIN. Switching means re-creating splits (rule H3).

---
## Phase 0 — Scaffold + environment
Prompt: "Do phase 0. Follow AGENTS.md. Stop after the checklist."
Skills: git-checkpoint, state-and-decisions
Do:
- Create folders: configs, data/raw, data/manifest, data/cache, splits, src, tests, results,
  figures, logs, models, notebooks, scripts.
- .gitignore: data/, models/, logs/, *.fits, *.zip, *.npy, *.pt, .venv/, __pycache__/, .ipynb_checkpoints/
- src/check_env.py: print python/torch/astropy/sklearn versions, CUDA yes/no,
  whether LENS_DATA_ROOT exists, and how many .fits files it finds.
- results/runs.csv with header (see skills/training-and-eval.md). figures/INDEX.md (empty list).
- pytest runs (even with 0 tests).
Figures: none.
Checklist:
- [ ] python src/check_env.py runs and its output is copied into STATE.md Environment
- [ ] git push works; data/ is ignored (git status shows no data)
- [ ] STATE.md Next action says "do phase 1"

---
## Phase 1 — Data inspection
Prompt: "Do phase 1. Follow AGENTS.md. Stop after the checklist and tell me which figures to open."
Skills: fits-and-data, visualization, commenting-and-explaining, state-and-decisions
Do:
- Scan LENS_DATA_ROOT, parse filenames (regex in skill), write data/manifest/manifest.csv:
  one row per object: obj_key, pipeline, cls, id, path_g..path_y, n_bands.
- List objects missing bands.
- Inspect 3 files: fits.info, HDU layout, shape, dtype, header keys. Record in STATE.md.
- Per band and per pipeline, on <= 500 objects: median, MAD, min, max, NaN count.
- Open the label tables: list columns; find any doubles/quads flag and contaminant type.
- Resolve the count mismatch (100k training images vs 50k x 4 simsets).
Figures (the owner must SEE lenses):
- phase1_grid_lenses.png: per pipeline, 4 lenses x 5 bands (asinh stretch)
- phase1_grid_nonlenses.png: same for non-lenses
- phase1_rgb_examples.png: g-r-i color composites, lens vs non-lens, both pipelines
- phase1_band_stats.png: histograms of per-image median and noise per band per pipeline
Checklist:
- [ ] Manifest complete (missing bands listed, if any)
- [ ] Cutout size, dtype, FITS layout recorded as verified facts
- [ ] Label tables understood; doubles/quads flag found or "not available" recorded
- [ ] Count mismatch explained
- [ ] Owner has looked at the figures

---
## Phase 2 — Dataset, splits, leakage tests
Prompt: "Do phase 2. Follow AGENTS.md. Stop after the checklist."
Skills: fits-and-data, preprocessing-and-augmentation, leakage-guard, visualization, commenting-and-explaining
Do:
- src/data.py: load_object -> float32 tensor (5, H, W), normalized per image; Dataset class;
  augmentation (train only).
- src/splits.py: 70/15/15 train/val/holdout, grouped by obj_key, stratified by (pipeline, cls),
  seeded; save splits/splits.csv.
- tests/: no leakage across splits; tensor shape; no NaN after normalization; augmentation
  identical across bands; labels derived from key.
- Optional cache of normalized tensors for the subset in use (data/cache/, gitignored).
Figures:
- phase2_normalization_before_after.png
- phase2_augmentation_demo.png: one lens, 8 flips/rotations, all 5 bands move together
- phase2_split_counts.png: bar chart of counts per split x pipeline x class
Checklist:
- [ ] pytest all green, including the leakage test
- [ ] Split counts balanced per pipeline and class
- [ ] Augmentation figure shows bands stay aligned
- [ ] Note in STATE: official lens-poor validation set, when released, is EVAL-ONLY

---
## Phase 3 — Baselines + shortcut checks
Prompt: "Do phase 3. Follow AGENTS.md. Stop after the checklist and explain results simply."
Skills: leakage-guard, training-and-eval, visualization
Do:
- Summary-statistic features per object (per band: median, std, max, central 5x5 sum,
  border mean, count of pixels above 3 sigma). Models: logistic regression and
  HistGradientBoostingClassifier.
- Pipeline detector: same features, predict D1 vs D2.
Figures:
- phase3_stats_baseline_roc.png
- phase3_feature_importance.png
- phase3_pipeline_detector.png (AUC and feature importance)
Checklist:
- [ ] AUCs stated in STATE.md
- [ ] If the trivial lens-vs-non-lens AUC is high (suspicious, e.g. > 0.9), flagged to the owner
      with a hypothesis (noise level? border? brightness?) and logged in DECISIONS.md
- [ ] If the pipeline detector is near-perfect, noted as a domain-shift warning for Phase 7

---
## Phase 4 — Small CNN baseline
Prompt: "Do phase 4. Follow AGENTS.md. Stop after the checklist."
Skills: training-and-eval, visualization, commenting-and-explaining
Do:
- src/models.py SmallCNN (3-4 conv blocks, global pool, 1 logit); src/train.py config-driven;
  src/evaluate.py (all H8 metrics, per pipeline).
- Smoke test, then 3 seeds on the small dataset. Log every run in results/runs.csv.
- If the run is too slow on CPU, write docs/COLAB_RUN.md with a ready-to-paste Colab cell block.
Figures:
- phase4_curves.png (loss and AUC per epoch)
- phase4_roc_pr.png
- phase4_score_hist.png (lens vs non-lens)
- phase4_gallery_TP_FP_FN_TN.png (16 each, with scores)
Checklist:
- [ ] 3 seeds in runs.csv with mean +/- std
- [ ] TPR@FPR numbers reported per pipeline
- [ ] Gallery inspected by the owner
- [ ] Not suspiciously better than the Phase 3 baselines without an explanation

---
## Phase 5 — ResNet-18 scratch vs pretrained (Experiment C)
Prompt: "Do phase 5. Follow AGENTS.md. Stop after the checklist."
Skills: training-and-eval, visualization
Do:
- SCALE-UP FIRST (owner has downloaded the main dataset, or agreed a fixed stratified random subset of it):
  re-run the manifest scan (Phase 1 code) and re-create splits from MAIN only (Phase 2 code); re-run tests;
  re-run the Phase 4 CNN once on main as a sanity check. From here to Phase 8 the data source stays
  MAIN (same splits). Never mix in small-dataset results (H3). Log as LOCKED decision.
- ResNet-18 adapted to 5 channels (code in skill). Two variants: random init and ImageNet init.
- Identical data, splits, epochs, lr, augmentation. 3 seeds each.
- Decide the default model for later phases; log as LOCKED in DECISIONS.md.
Figures: phase5_scratch_vs_pretrained.png (bars with error bars), phase5_curves.png
Checklist:
- [ ] Only the init differs between the two variants
- [ ] Mean +/- std over 3 seeds
- [ ] Default model chosen and LOCKED

---
## Phase 6 — Experiment A: which bands matter
Prompt: "Do phase 6. Follow AGENTS.md. Stop after the checklist."
Skills: training-and-eval, visualization
Do:
- Default model from Phase 5. Band sets: g, r, i, z, y individually; gri; grizy. 3 seeds each.
- Same splits for every variant (H1, H3).
Figures: phase6_band_sets.png (AUC and TPR@FPR per band set, error bars)
Checklist:
- [ ] All band sets use identical splits and hyperparameters
- [ ] Table saved to results/phase6_bands.csv
- [ ] One-paragraph reading of the result in STATE.md

---
## Phase 7 — Experiment B: pipeline transfer
Prompt: "Do phase 7. Follow AGENTS.md. Stop after the checklist."
Skills: training-and-eval, leakage-guard, visualization
Do:
- Train on D1 only, D2 only, and both. Evaluate each on D1 and D2 (same held-out objects).
- 3 seeds each.
Figures: phase7_transfer_heatmap.png (AUC and TPR@FPR, rows = train, cols = test)
Checklist:
- [ ] 3x2 matrix complete with mean +/- std
- [ ] Off-diagonal drop quantified and written in plain words in STATE.md
- [ ] If an official realistic validation set exists, evaluated there too (eval-only)

---
## Phase 8 — Failure analysis + prior-shift table (Experiment D)
Prompt: "Do phase 8. Follow AGENTS.md. Stop after the checklist."
Skills: training-and-eval, visualization
Do:
- Break errors down by doubles vs quads and by contaminant type, if label tables allow
  (otherwise say so). Per pipeline too.
- Table: precision at true lens fractions pi in {50%, 10%, 1%, 0.1%} from measured TPR and FPR
  (precision = TPR*pi / (TPR*pi + FPR*(1-pi))).
Figures:
- phase8_top_false_positives.png and phase8_top_false_negatives.png (20 each, scores shown)
- phase8_error_breakdown.png
- phase8_precision_vs_prevalence.png
Checklist:
- [ ] Owner looked at the galleries and gave 3 plain observations (agent records them)
- [ ] Prior-shift table saved to results/

---
## Phase 9 — Test predictions + submission (only when the test set is released)
Prompt: "Do phase 9. Follow AGENTS.md. First ask me to paste the submission rules."
Skills: fits-and-data, training-and-eval, preprocessing-and-augmentation
Do:
- Ask the owner to paste the Evaluation and Submission text. Record in STATE.md.
- Test filenames carry only the band: work out how bands are grouped into objects (inspect; ask if unclear).
- src/predict.py: ensemble of seeds + 8-way flip/rotation test-time augmentation; sanity checks
  (no NaN, every ID present, score distribution sane, same preprocessing as training).
- Write the submission file in the official format. Draft a <= 200-word methodology blurb.
Checklist:
- [ ] Submission format verified against the rules
- [ ] Score histogram looks sane (not all one value)
- [ ] Owner uploads the file himself

---
## Phase 10 — Write-up + polish
Prompt: "Do phase 10. Follow AGENTS.md. Stop after the checklist."
Skills: visualization, commenting-and-explaining, git-checkpoint
Do:
- scripts/make_results_tables.py -> README results tables from results/runs.csv.
- README.md: question, data, method, results with figures, how to reproduce.
- LIMITATIONS.md: simulated data only, assumptions, what was not tested.
- docs/blog_outline.md: outline only (hook, question, what I did, 3 findings, caveats, next steps).
- Verify reproduction from a clean clone (commands in README run).
- Tag phase-10-done.
Checklist:
- [ ] README commands work from scratch
- [ ] Every claim in README matches runs.csv
- [ ] Claims say "in these simulations"

---
## Phase S (stretch, only if A-D finished) — color-consistency feature
Prompt: "Do phase S. Follow AGENTS.md."
Idea: lensed images of one quasar share a color. Add a hand-built color-consistency feature to
the CNN. Test whether it adds ANYTHING beyond the 5-band CNN (same splits, 3 seeds). A null result is fine.
