"""Resolved locations for the example tree."""

from pathlib import Path

EXAMPLES_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXAMPLES_ROOT.parent
DATA_DIR = EXAMPLES_ROOT / "data"
FINETUNE_DIR = DATA_DIR / "finetune"
OUTPUT_DIR = EXAMPLES_ROOT / "output"
