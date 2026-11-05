# Skill: preprocessing-and-augmentation
Use when: building data.py, Dataset, TTA.

## Per-image normalization (LOCKED D-002)
Why: pixel values span a huge range. A few very bright pixels (point-source cores) would dominate.
MAD is a noise estimate that outliers don't distort. arcsinh compresses bright values but keeps faint structure.
```python
import numpy as np
def normalize_band(img):
    img = np.nan_to_num(img.astype("float32"), nan=0.0, posinf=0.0, neginf=0.0)  # log counts elsewhere
    med = np.median(img)
    mad = 1.4826 * np.median(np.abs(img - med)) + 1e-8      # ~ noise sigma
    return np.arcsinh((img - med) / mad)
def load_object(paths_by_band):                              # order: g r i z y (H16)
    return np.stack([normalize_band(read(paths_by_band[b])) for b in "grizy"])   # (5, H, W)
```
Optional extra: clip to a fixed range after arcsinh (log it in DECISIONS.md if used).

## Augmentation (LOCKED D-003): train split only
Lensing has no preferred orientation, so flips and 90-degree rotations are safe.
The SAME transform must hit all 5 bands, otherwise colors/positions break.
```python
import torch
def d4_augment(x, rng):                 # x: tensor (5, H, W)
    x = torch.rot90(x, int(rng.integers(0, 4)), dims=(1, 2))
    if rng.random() < 0.5:
        x = torch.flip(x, dims=(2,))
    return x
```
Never: brightness/contrast/color jitter, random crops, per-band transforms. Shifts: not in v1.

## Test-time augmentation (Phase 9)
Average the model output over the 8 D4 variants (4 rotations x optional flip).
