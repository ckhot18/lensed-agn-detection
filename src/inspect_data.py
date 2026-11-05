"""Build the Phase 1 manifest and make visual checks of the small FITS dataset."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.visualization import make_lupton_rgb
from scipy.ndimage import gaussian_filter

# Beginner note: a band is one colour filter.  Five bands observe the same object.
BANDS = ("g", "r", "i", "z", "y")
NAME = re.compile(r"D(?P<pipe>[12])_(?P<cls>[NL])(?P<oid>\d{8})_(?P<band>[grizy])\.fits$")


def parse_file(path: Path) -> dict[str, str] | None:
    """What: read object identity from one FITS filename. Why: filenames hold Phase 1 labels.
    In: path, a FITS filename. Out: identity dictionary, or None when the name is unrelated."""
    match = NAME.fullmatch(path.name)
    if match is None:
        return None
    item = match.groupdict()
    item["pipeline"] = f"D{item.pop('pipe')}"
    item["id"] = item.pop("oid")
    item["obj_key"] = f"{item['pipeline']}_{item['cls']}_{item['id']}"
    return item


def build_manifest(data_root: Path, limit: int | None = None) -> pd.DataFrame:
    """What: group five band files into one object row. Why: later phases must split objects.
    In: data_root and optional file limit. Out: one row per object with five path columns."""
    objects: dict[str, dict[str, str]] = {}
    for path in sorted(data_root.rglob("*.fits"))[:limit]:
        item = parse_file(path)
        if item is None:
            continue
        row = objects.setdefault(item["obj_key"], {key: item[key] for key in ("obj_key", "pipeline", "cls", "id")})
        row[f"path_{item['band']}"] = str(path.resolve())
    rows = []
    for row in objects.values():
        row["n_bands"] = sum(pd.notna(row.get(f"path_{band}")) for band in BANDS)
        rows.append(row)
    return pd.DataFrame(rows, columns=["obj_key", "pipeline", "cls", "id", *[f"path_{b}" for b in BANDS], "n_bands"]).sort_values("obj_key")


def read_image(path: str) -> np.ndarray:
    """What: load a FITS primary image as float32. Why: statistics and plots need numeric arrays.
    In: path to an image FITS file. Out: image array (H, W), float32."""
    with fits.open(path, memmap=False) as hdul:
        return np.asarray(hdul[0].data, dtype=np.float32)


def robust_values(image: np.ndarray) -> tuple[float, float, float, float, int]:
    """What: calculate safe image summary values. Why: bad pixels must be counted explicitly.
    In: image, array (H, W). Out: median, MAD, min, max, and non-finite-pixel count."""
    finite = image[np.isfinite(image)]
    if finite.size == 0:
        return np.nan, np.nan, np.nan, np.nan, int(image.size)
    median = float(np.median(finite))
    mad = float(np.median(np.abs(finite - median)))
    return median, mad, float(finite.min()), float(finite.max()), int(image.size - finite.size)


def sampled_rows(manifest: pd.DataFrame, per_pipeline: int) -> pd.DataFrame:
    """What: choose up to a balanced fixed sample per pipeline. Why: Phase 1 avoids reading all images.
    In: manifest and object cap. Out: reproducible object rows, no more than cap each pipeline."""
    chosen = []
    for _, pipeline_rows in manifest.groupby("pipeline", sort=True):
        classes = [group for _, group in pipeline_rows.groupby("cls", sort=True)]
        cap = max(1, per_pipeline // len(classes))
        chosen.extend(group.sort_values("obj_key").head(cap).to_dict("records") for group in classes)
    return pd.DataFrame([row for group in chosen for row in group])


def collect_stats(rows: pd.DataFrame) -> pd.DataFrame:
    """What: summarize every selected image by pipeline and band. Why: reveal scale and bad pixels.
    In: object rows with paths. Out: one row per image with robust summary values."""
    records = []
    for _, row in rows.iterrows():
        for band in BANDS:
            image = read_image(row[f"path_{band}"])
            median, mad, minimum, maximum, nonfinite = robust_values(image)
            records.append({"pipeline": row.pipeline, "cls": row.cls, "band": band, "median": median,
                            "mad": mad, "min": minimum, "max": maximum, "nonfinite": nonfinite})
    return pd.DataFrame(records)


def stretched(image: np.ndarray) -> np.ndarray:
    """What: make a safe display stretch. Why: raw astronomy pixels often look black on screen.
    In: image, array (H, W). Out: display array (H, W), clipped from 0 to 1."""
    finite = image[np.isfinite(image)]
    low, high = np.percentile(finite, (1, 99.5))
    return np.clip((np.arcsinh(image) - np.arcsinh(low)) / (np.arcsinh(high) - np.arcsinh(low) + 1e-8), 0, 1)


def save_band_grid(manifest: pd.DataFrame, cls: str, destination: Path) -> None:
    """What: plot four examples per pipeline across five bands. Why: visually check labels and alignment.
    In: manifest, class letter, output PNG. Out: saved 8-by-5 image grid."""
    rows = manifest[manifest.cls.eq(cls)].groupby("pipeline", sort=True).head(4).reset_index(drop=True)
    fig, axes = plt.subplots(len(rows), len(BANDS), figsize=(12, 15), constrained_layout=True)
    for row_index, row in rows.iterrows():
        for band_index, band in enumerate(BANDS):
            axes[row_index, band_index].imshow(stretched(read_image(row[f"path_{band}"])), cmap="gray", origin="lower")
            axes[row_index, band_index].set_title(f"{row.pipeline} {'lens' if cls == 'L' else 'non-lens'} {row.id}\n{band}")
            axes[row_index, band_index].set_axis_off()
    fig.savefig(destination, dpi=150)
    plt.close(fig)


def normalized(image: np.ndarray) -> np.ndarray:
    """What: centre an image and scale by MAD. Why: RGB colours need comparable noise units.
    In: image, array (H, W). Out: noise-scaled image (H, W)."""
    median, mad, _, _, _ = robust_values(image)
    return (image - median) / (1.4826 * mad + 1e-8)


def display_rgb_band(image: np.ndarray) -> np.ndarray:
    """What: lightly smooth a noise-scaled band for RGB display. Why: colours should show objects, not pixels.
    In: image, array (H, W). Out: smoothed noise-scaled image (H, W)."""
    return gaussian_filter(normalized(image), sigma=0.75)


def save_rgb_examples(manifest: pd.DataFrame, destination: Path) -> None:
    """What: show one RGB composite for each pipeline and class. Why: colour differences are evidence.
    In: manifest and output PNG. Out: saved two-by-two composite figure."""
    fig, axes = plt.subplots(2, 2, figsize=(8, 8), constrained_layout=True)
    for row_index, pipeline in enumerate(("D1", "D2")):
        for col_index, cls in enumerate(("L", "N")):
            row = manifest[(manifest.pipeline == pipeline) & (manifest.cls == cls)].iloc[0]
            rgb = make_lupton_rgb(display_rgb_band(read_image(row.path_i)), display_rgb_band(read_image(row.path_r)), display_rgb_band(read_image(row.path_g)), stretch=3, Q=8)
            axes[row_index, col_index].imshow(rgb, origin="lower")
            axes[row_index, col_index].set_title(f"{pipeline} {'lens' if cls == 'L' else 'non-lens'} {row.id}")
            axes[row_index, col_index].set_axis_off()
    fig.savefig(destination, dpi=150)
    plt.close(fig)


def save_stats(stats: pd.DataFrame, destination: Path) -> None:
    """What: histogram image backgrounds and noise by band/pipeline. Why: compare input distributions.
    In: per-image summary table. Out: saved two-panel histogram figure."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), constrained_layout=True)
    for row_index, column in enumerate(("median", "mad")):
        for col_index, pipeline in enumerate(("D1", "D2")):
            subset = stats[stats.pipeline.eq(pipeline)]
            for band in BANDS:
                axes[row_index, col_index].hist(subset[subset.band.eq(band)][column], bins=35, histtype="step", label=band)
            axes[row_index, col_index].set_title(f"{pipeline}: per-image {column}")
            axes[row_index, col_index].set_xlabel(column)
            axes[row_index, col_index].set_ylabel("number of images")
            axes[row_index, col_index].legend(title="band")
    fig.savefig(destination, dpi=150)
    plt.close(fig)


def main() -> None:
    """What: run the Phase 1 inspection. Why: make data facts reproducible before model work.
    In: CLI options and LENS_DATA_ROOT. Out: manifest, report, and optional figures."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/manifest/manifest.csv"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--stats-per-pipeline", type=int, default=500)
    parser.add_argument("--no-figures", action="store_true")
    args = parser.parse_args()
    root = os.environ.get("LENS_DATA_ROOT")
    if not root or not Path(root).is_dir():
        raise SystemExit("Set LENS_DATA_ROOT to the unzipped FITS directory first.")
    manifest = build_manifest(Path(root), args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(args.output, index=False)
    missing = manifest[manifest.n_bands.ne(5)].obj_key.tolist()
    stats = collect_stats(sampled_rows(manifest, args.stats_per_pipeline))
    class_counts = {f"{pipe}_{cls}": int(count) for (pipe, cls), count in manifest.groupby(["pipeline", "cls"]).size().items()}
    summary = stats.groupby(["pipeline", "band"])[["median", "mad", "min", "max", "nonfinite"]].agg(["median", "min", "max"]).reset_index()
    summary.columns = ["_".join(part for part in column if part) if isinstance(column, tuple) else column for column in summary.columns]
    report = {"objects": len(manifest), "objects_by_pipeline_class": class_counts,
              "missing_band_objects": missing, "stats_summary": summary.to_dict(orient="records")}
    args.output.with_name("inspection_report.json").write_text(json.dumps(report, indent=2, default=str))
    print(f"Objects: {len(manifest)}; missing all-five-band objects: {len(missing)}")
    print(f"Objects by pipeline/class: {report['objects_by_pipeline_class']}")
    print(f"Non-finite pixels in sampled images: {int(stats.nonfinite.sum())}")
    if not args.no_figures:
        save_band_grid(manifest, "L", Path("figures/phase1_grid_lenses.png"))
        save_band_grid(manifest, "N", Path("figures/phase1_grid_nonlenses.png"))
        save_rgb_examples(manifest, Path("figures/phase1_rgb_examples.png"))
        save_stats(stats, Path("figures/phase1_band_stats.png"))


if __name__ == "__main__":
    main()
