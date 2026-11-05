"""Create one reproducible object-level split from the Phase 1 manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def make_splits(manifest: pd.DataFrame, seed: int, fractions: dict[str, float]) -> pd.DataFrame:
    """What: stratify whole objects into train/val/holdout. Why: no band's sibling may leak splits.
    In: manifest rows, seed, fraction mapping. Out: obj_key/split table with one row per object."""
    if not np.isclose(sum(fractions.values()), 1.0):
        raise ValueError("Split fractions must add to 1.0")
    rng = np.random.default_rng(seed)
    pieces = []
    for _, group in manifest.groupby(["pipeline", "cls"], sort=True):
        keys = group.obj_key.to_numpy(copy=True)
        rng.shuffle(keys)
        train_end = int(len(keys) * fractions["train"])
        val_end = train_end + int(len(keys) * fractions["val"])
        for split, part in (("train", keys[:train_end]), ("val", keys[train_end:val_end]), ("holdout", keys[val_end:])):
            pieces.append(pd.DataFrame({"obj_key": part, "split": split}))
    return pd.concat(pieces, ignore_index=True).sort_values("obj_key").reset_index(drop=True)


def create_or_load(manifest: pd.DataFrame, output: Path, seed: int, fractions: dict[str, float]) -> pd.DataFrame:
    """What: reuse an existing split or make it once. Why: silent re-splitting breaks fair experiments.
    In: manifest, output path, seed, fractions. Out: validated split table."""
    if output.exists():
        splits = pd.read_csv(output)
        if set(splits.obj_key) != set(manifest.obj_key) or not splits.obj_key.is_unique:
            raise ValueError("Existing split does not match this manifest; do not overwrite it silently.")
        return splits
    splits = make_splits(manifest, seed, fractions)
    output.parent.mkdir(parents=True, exist_ok=True)
    splits.to_csv(output, index=False)
    return splits


def main() -> None:
    """What: create the configured split file. Why: make the split recipe runnable from one command.
    In: YAML config path. Out: saved/reused split CSV and printed group counts."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/splits.yaml"))
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())
    manifest = pd.read_csv(config["manifest"])
    if not manifest.n_bands.eq(5).all():
        raise ValueError("Manifest has incomplete objects; repair it before splitting.")
    splits = create_or_load(manifest, Path(config["output"]), int(config["seed"]), config["fractions"])
    counts = manifest.merge(splits, on="obj_key").groupby(["split", "pipeline", "cls"]).size()
    print(counts.to_string())


if __name__ == "__main__":
    main()
