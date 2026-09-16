"""Resolve example data paths from any working directory."""

from __future__ import annotations

from pathlib import Path

EXAMPLES_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = EXAMPLES_ROOT.parent
DATA_DIR = EXAMPLES_ROOT / "data"
SPLITS_DIR = DATA_DIR / "splits"
OUTPUT_DIR = EXAMPLES_ROOT / "output"
