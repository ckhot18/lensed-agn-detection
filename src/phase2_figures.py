"""Make the reproducible Phase 2 normalization, augmentation, and split figures."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from astropy.io import fits

from src.data import BANDS, apply_d4, load_object


def stretch(image: np.ndarray) -> np.ndarray:
    """What: scale one displayed image into 0..1. Why: raw FITS brightness is hard to see.
    In: image (H, W). Out: clipped display image (H, W)."""
    low, high = np.percentile(image[np.isfinite(image)], (1, 99.5))
    return np.clip((image - low) / (high - low + 1e-8), 0, 1)


def first_lens(manifest: pd.DataFrame) -> pd.Series:
    """What: select a fixed lens example. Why: figures must reproduce exactly on every rerun.
    In: manifest rows. Out: earliest D1 lens row, or earliest available lens row."""
    lenses = manifest[manifest.cls.eq("L")].sort_values(["pipeline", "obj_key"])
    if lenses.empty:
        raise ValueError("A lens example is required for Phase 2 figures.")
    return lenses.iloc[0]


def save_normalization(manifest: pd.DataFrame, destination: Path) -> None:
    """What: compare raw and normalized five-band views. Why: make preprocessing visible to the owner.
    In: manifest and PNG path. Out: saved two-by-five panel figure."""
    row = first_lens(manifest)
    normalized = load_object(row).numpy()
    fig, axes = plt.subplots(2, 5, figsize=(12, 5), constrained_layout=True)
    for index, band in enumerate(BANDS):
        raw = fits.getdata(row[f"path_{band}"])
        axes[0, index].imshow(stretch(raw), cmap="gray", origin="lower")
        axes[1, index].imshow(stretch(normalized[index]), cmap="gray", origin="lower")
        axes[0, index].set_title(f"raw {band}")
        axes[1, index].set_title(f"normalized {band}")
        axes[0, index].set_axis_off(); axes[1, index].set_axis_off()
    fig.suptitle(f"{row.pipeline} lens {row.id}: per-image median/MAD + asinh", fontsize=13)
    fig.savefig(destination, dpi=150)
    plt.close(fig)


def save_augmentation(manifest: pd.DataFrame, destination: Path) -> None:
    """What: show all eight shared D4 transformations. Why: verify every band moves together.
    In: manifest and PNG path. Out: saved eight-by-five panel figure."""
    row = first_lens(manifest)
    image = load_object(row).numpy()
    fig, axes = plt.subplots(8, 5, figsize=(10, 16), constrained_layout=True)
    for variant, (rotation, flip) in enumerate((rotation, flip) for flip in (False, True) for rotation in range(4)):
        transformed = apply_d4(torch.from_numpy(image), rotation, flip).numpy()
        for index, band in enumerate(BANDS):
            axes[variant, index].imshow(stretch(transformed[index]), cmap="gray", origin="lower")
            axes[variant, index].set_title(f"{band}: r={rotation * 90}°, flip={flip}" if index == 0 else band, fontsize=8)
            axes[variant, index].set_axis_off()
    fig.suptitle(f"{row.pipeline} lens {row.id}: each row applies one shared transform to g,r,i,z,y", fontsize=12)
    fig.savefig(destination, dpi=150)
    plt.close(fig)


def save_split_counts(manifest: pd.DataFrame, splits: pd.DataFrame, destination: Path) -> None:
    """What: bar-chart split counts by pipeline/class. Why: verify stratification stayed balanced.
    In: manifest, split table, PNG path. Out: saved labelled count chart."""
    joined = manifest.merge(splits, on="obj_key", validate="one_to_one")
    counts = joined.groupby(["split", "pipeline", "cls"]).size().unstack(["pipeline", "cls"])
    counts = counts.reindex(["train", "val", "holdout"])
    axis = counts.plot.bar(figsize=(10, 6), rot=0)
    axis.set_title("Object counts by split, pipeline, and class")
    axis.set_xlabel("split"); axis.set_ylabel("objects")
    axis.legend(title="pipeline, class", ncols=2)
    axis.figure.tight_layout()
    axis.figure.savefig(destination, dpi=150)
    plt.close(axis.figure)


def main() -> None:
    """What: generate all Phase 2 figures. Why: make checks repeatable from saved manifest/split files.
    In: manifest and split CSV paths. Out: three phase2 PNGs in the figures directory."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data/manifest/manifest.csv"))
    parser.add_argument("--splits", type=Path, default=Path("splits/splits.csv"))
    args = parser.parse_args()
    manifest, splits = pd.read_csv(args.manifest), pd.read_csv(args.splits)
    Path("figures").mkdir(exist_ok=True)
    save_normalization(manifest, Path("figures/phase2_normalization_before_after.png"))
    save_augmentation(manifest, Path("figures/phase2_augmentation_demo.png"))
    save_split_counts(manifest, splits, Path("figures/phase2_split_counts.png"))


if __name__ == "__main__":
    main()
