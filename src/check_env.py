"""Print the small set of environment facts needed before Phase 1."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def version_or_missing(module_name: str) -> str:
    """Return a package version without making a missing package a crash."""
    try:
        module = __import__(module_name)
        return str(module.__version__)
    except ImportError:
        return "not installed"


def count_fits(data_root: Path | None) -> int:
    """Count FITS files beneath the configured data root, if it exists."""
    if data_root is None or not data_root.is_dir():
        return 0
    return sum(1 for _ in data_root.rglob("*.fits"))


def main() -> None:
    """Print versions and data availability in a copyable, stable format."""
    data_value = os.environ.get("LENS_DATA_ROOT")
    data_root = Path(data_value) if data_value else None
    print(f"Python: {sys.version.split()[0]}")
    print(f"torch: {version_or_missing('torch')}")
    print(f"astropy: {version_or_missing('astropy')}")
    print(f"sklearn: {version_or_missing('sklearn')}")
    import torch
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"LENS_DATA_ROOT: {data_value or 'not set'}")
    print(f"LENS_DATA_ROOT exists: {bool(data_root and data_root.is_dir())}")
    print(f"FITS files: {count_fits(data_root)}")


if __name__ == "__main__":
    main()
