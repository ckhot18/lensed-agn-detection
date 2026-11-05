# Skill: leakage-guard
Use when: splitting data, evaluating, or ever seeing a score that looks too good.

## Rules (see AGENTS.md H1-H3, H6, H7, H13)
- Split by OBJECT (obj_key), never by file. Stratify by (pipeline, cls). Seeded. Save once.
- One data source per experiment (small, main, or per-band: they overlap).
- Test filenames reveal only the band. Labels are never features.

## Split sketch
```python
import numpy as np, pandas as pd
def make_splits(manifest, seed=0, frac=(0.70, 0.15, 0.15)):
    rng = np.random.default_rng(seed)
    out = []
    for (pipe, cls), g in manifest.groupby(["pipeline", "cls"]):   # stratify
        keys = g["obj_key"].to_numpy().copy(); rng.shuffle(keys)
        n = len(keys); a = int(frac[0]*n); b = a + int(frac[1]*n)
        for name, part in (("train", keys[:a]), ("val", keys[a:b]), ("holdout", keys[b:])):
            out.append(pd.DataFrame({"obj_key": part, "split": name}))
    return pd.concat(out)            # then save to splits/splits.csv
```

## Required test (tests/test_no_leakage.py)
```python
def test_no_overlap():
    df = pd.read_csv("splits/splits.csv")
    s = {k: set(df[df.split == k].obj_key) for k in ["train", "val", "holdout"]}
    assert not (s["train"] & s["val"]) and not (s["train"] & s["holdout"]) and not (s["val"] & s["holdout"])
    assert df.obj_key.is_unique          # one object, one split
```

## Shortcut checks (Phase 3, repeat whenever data changes)
1. Summary-stat model (per-band median, std, max, border mean, central sum, NaN count) -> lens vs not.
   High AUC means the label is guessable without lens physics. STOP and report.
2. Pipeline detector: can stats/CNN tell D1 from D2? If yes, a CNN can too: domain-shift warning.
3. Check ID/file order vs class (rule H13). Always shuffle training data.
4. Normalization statistics from TRAIN only. Per-image normalization needs none.
5. Never tune thresholds or hyperparameters on holdout.
