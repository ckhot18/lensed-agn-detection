"""Load five-band FITS objects with the locked normalization and augmentation rules."""

from __future__ import annotations

import re
from collections.abc import Mapping

import numpy as np
import torch
from astropy.io import fits
from torch.utils.data import Dataset

# Beginner note: a band is one colour filter. Channel order must always stay g, r, i, z, y.
BANDS = ("g", "r", "i", "z", "y")
KEY = re.compile(r"^D[12]_([NL])_\d{8}$")


def normalize_band(image: np.ndarray) -> np.ndarray:
    """What: centre one image and compress bright values. Why: bright cores must not dominate faint structure.
    In: image, array (H, W). Out: finite float32 array (H, W) after median/MAD/asinh normalization."""
    clean = np.nan_to_num(image.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    median = np.median(clean)
    # Beginner note: MAD is a noise estimate that is not pulled strongly by bright sources.
    noise = 1.4826 * np.median(np.abs(clean - median)) + 1e-8
    return np.arcsinh((clean - median) / noise).astype(np.float32)


def load_object(paths_by_band: Mapping[str, str]) -> torch.Tensor:
    """What: load and normalize a five-band object. Why: the model needs one aligned tensor per object.
    In: path mapping with g,r,i,z,y keys. Out: float32 tensor (5, H, W), ordered g,r,i,z,y."""
    arrays = []
    for band in BANDS:
        with fits.open(paths_by_band[f"path_{band}"], memmap=False) as hdul:
            arrays.append(normalize_band(hdul[0].data))
    return torch.from_numpy(np.stack(arrays, axis=0))  # (5, H, W)


def label_from_key(obj_key: str) -> int:
    """What: turn the filename class letter into y. Why: labels must never enter image features.
    In: obj_key like D1_L_00000042. Out: 1 for lens or 0 for non-lens."""
    match = KEY.fullmatch(obj_key)
    if match is None:
        raise ValueError(f"Unexpected object key: {obj_key}")
    return int(match.group(1) == "L")


def apply_d4(x: torch.Tensor, rotation: int, flip: bool) -> torch.Tensor:
    """What: apply one shared rotation/flip to five channels. Why: colour alignment is scientific evidence.
    In: x tensor (5, H, W), rotation 0..3, flip flag. Out: transformed tensor (5, H, W)."""
    result = torch.rot90(x, rotation, dims=(1, 2))
    return torch.flip(result, dims=(2,)) if flip else result


def d4_augment(x: torch.Tensor, rng: np.random.Generator) -> torch.Tensor:
    """What: draw one of eight D4 transforms. Why: lens orientation has no preferred direction.
    In: x tensor (5, H, W) and seeded random generator. Out: transformed tensor (5, H, W)."""
    return apply_d4(x, int(rng.integers(0, 4)), bool(rng.integers(0, 2)))


class LensDataset(Dataset):
    """What: expose manifest rows as tensors and labels. Why: PyTorch training needs a stable interface.
    In: rows table, train flag, seed. Out: dictionaries with x (5,H,W), y scalar, and obj_key."""

    def __init__(self, rows, train: bool = False, seed: int = 0):
        self.rows = rows.reset_index(drop=True)
        self.train = train
        self.seed = seed
        self.epoch = 0

    def set_epoch(self, epoch: int) -> None:
        """What: set the augmentation epoch. Why: same seed gives the same transforms on reruns.
        In: epoch integer. Out: no return; later samples use this epoch in their random seed."""
        self.epoch = epoch

    def __len__(self) -> int:
        """What: report object count. Why: PyTorch uses it to index the dataset. In: none. Out: count."""
        return len(self.rows)

    def __getitem__(self, index: int) -> dict:
        """What: load one object and its filename-derived label. Why: keep features and labels separate.
        In: integer index. Out: x (5,H,W), y scalar tensor, and obj_key string."""
        row = self.rows.iloc[index]
        x = load_object(row)
        if self.train:
            rng = np.random.default_rng(np.random.SeedSequence([self.seed, self.epoch, index]))
            x = d4_augment(x, rng)
        return {"x": x, "y": torch.tensor(label_from_key(row.obj_key), dtype=torch.long), "obj_key": row.obj_key}
