#!/usr/bin/env python3
"""Regenerate the sample CSVs and refuse to write a broken schema."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fjordpress.cli import main
from fjordpress.csvio import read_csv
from fjordpress.paths import data_dir
from fjordpress.schemas import validate_columns

CHECKS = {
    "00_raw_articles.csv": "raw_input",
    "01_translated_articles.csv": "translated",
    "02_summarised_articles.csv": "summarised",
    "03_labeled_dataset.csv": "labeled",
    "04_train_dataset.csv": "split",
    "05_public_eval_shape.csv": "public_eval",
}


if __name__ == "__main__":
    code = main(["fixtures"])
    if code != 0:
        raise SystemExit(code)
    root = data_dir()
    for name, schema in CHECKS.items():
        rows = read_csv(root / name)
        validate_columns(rows[0].keys(), schema)
        print(f"ok  {name:28} {schema:12} {len(rows)} rows")
    raise SystemExit(0)
