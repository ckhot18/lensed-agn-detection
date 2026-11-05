# DECISIONS.md — decision log (agent: APPEND only; <= 6 lines per entry)
Entry format:
### D-0XX | phase N | date | LOCKED? 
- Decision:
- Options considered:
- Why:
- Impact / how to undo:

Log: every choice between options, every deviation from PHASES.md, every bug found + fix,
every surprising result. Do not edit old entries; add a new one that supersedes.

---
### D-001 | planning | 2026-11-05 | LOCKED
- Decision: Split by object key (pipeline_cls_id); all 5 bands together; saved to splits/splits.csv.
- Why: prevents leakage across band files (rule H1).

### D-002 | planning | 2026-11-05 | LOCKED
- Decision: Per-image normalization: subtract median, divide by 1.4826*MAD, then arcsinh.
- Why: huge dynamic range; no dataset statistics needed, so no leakage (H4).

### D-003 | planning | 2026-11-05 | LOCKED
- Decision: Augment with flips and 90-degree rotations only, same transform on all 5 bands.
- Why: lensing has no preferred orientation; color must stay intact (H5).

### D-004 | planning | 2026-11-05 | LOCKED
- Decision: Metrics = AUC, average precision, TPR@FPR 1e-2 and 1e-3, per pipeline and overall.
- Why: training is 50/50 but real data is lens-poor (H8).

### D-005 | planning | 2026-11-05 | LOCKED
- Decision: Research question = robustness across pipelines via four experiments:
  A bands, B pipeline transfer, C ImageNet vs scratch, D failure analysis. Color-consistency
  feature is an optional stretch (Phase S).

### D-006 | planning | 2026-11-05
- Decision: Framework = PyTorch + torchvision. Develop on the small dataset, scale to main later.
- Why: small is ~350 MiB; main is ~17 GiB. Remember H3 when switching.

### D-007 | planning | 2026-11-05 | LOCKED
- Decision: Phases 0-4 on the small dataset; scale up to main (or a fixed stratified subset) at the start of Phase 5;
  Phases 5-8 all on main with the same splits.
- Why: small holdout is ~600 objects, too few for TPR@FPR=1e-3; all experiment comparisons must share one data source (H3).
- Impact: small-dataset numbers are for debugging only, never reported next to main results.
