"""Small deterministic checks for the Phase 2 loader and augmentation."""

import numpy as np
import pandas as pd
import torch
from astropy.io import fits

from src.data import apply_d4, label_from_key, load_object, normalize_band
from src.splits import make_splits


def test_normalization_removes_nonfinite_values():
    """What: normalize an image with bad pixels. Why: model tensors must be finite.
    In: image (3, 3) with NaN/inf. Out: finite float32 normalized image (3, 3)."""
    image = np.array([[np.nan, np.inf, -np.inf], [1, 2, 3], [4, 5, 6]], dtype=np.float64)
    result = normalize_band(image)
    assert result.dtype == np.float32
    assert np.isfinite(result).all()


def test_load_object_shape_and_finite_values(tmp_path):
    """What: load five temporary FITS bands. Why: channel order and shape are model contracts.
    In: five (41, 41) test files. Out: finite tensor (5, 41, 41)."""
    paths = {}
    for index, band in enumerate("grizy"):
        image = np.full((41, 41), index, dtype=np.float64)
        image[0, 0] = np.nan
        path = tmp_path / f"{band}.fits"
        fits.writeto(path, image)
        paths[f"path_{band}"] = str(path)
    result = load_object(paths)
    assert result.shape == (5, 41, 41)
    assert torch.isfinite(result).all()


def test_augmentation_moves_all_bands_together():
    """What: transform channel-coded patterns. Why: a transform must not separate band positions.
    In: tensor (5, 3, 3). Out: all channels match the same spatial transform."""
    base = torch.arange(9, dtype=torch.float32).reshape(1, 3, 3)
    image = torch.cat([base + 100 * channel for channel in range(5)])
    transformed = apply_d4(image, rotation=1, flip=True)
    expected = apply_d4(base, rotation=1, flip=True)[0]
    for channel in range(5):
        assert torch.equal(transformed[channel] - 100 * channel, expected)


def test_labels_are_derived_only_from_keys():
    """What: decode the class letter from keys. Why: labels are y, never image input features.
    In: valid lens and non-lens keys. Out: 1 for L and 0 for N."""
    assert label_from_key("D1_L_00000042") == 1
    assert label_from_key("D2_N_00000042") == 0


def test_no_object_leakage_and_stratified_counts():
    """What: split a balanced synthetic manifest. Why: prove objects never overlap between splits.
    In: 80 object rows across pipeline/class strata. Out: unique 70/15/15 object assignments."""
    rows = [{"obj_key": f"{pipe}_{cls}_{number:08d}", "pipeline": pipe, "cls": cls}
            for pipe in ("D1", "D2") for cls in ("L", "N") for number in range(20)]
    splits = make_splits(pd.DataFrame(rows), seed=7, fractions={"train": .7, "val": .15, "holdout": .15})
    assert splits.obj_key.is_unique
    assert splits.split.value_counts().to_dict() == {"train": 56, "val": 12, "holdout": 12}
    assert set(splits.split) == {"train", "val", "holdout"}
    repeated = make_splits(pd.DataFrame(rows), seed=7, fractions={"train": .7, "val": .15, "holdout": .15})
    pd.testing.assert_frame_equal(splits, repeated)


def test_saved_split_has_no_object_leakage():
    """What: inspect the saved Phase 2 object split. Why: the actual experiment split must not leak.
    In: splits/splits.csv. Out: one unique train, val, or holdout assignment per object."""
    splits = pd.read_csv("splits/splits.csv")
    groups = {name: set(splits[splits.split.eq(name)].obj_key) for name in ("train", "val", "holdout")}
    assert splits.obj_key.is_unique
    assert not (groups["train"] & groups["val"])
    assert not (groups["train"] & groups["holdout"])
    assert not (groups["val"] & groups["holdout"])
