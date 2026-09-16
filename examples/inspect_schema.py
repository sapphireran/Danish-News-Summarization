#!/usr/bin/env python3
"""Print and validate the CSV contracts used by the 2023 scripts.

    PYTHONPATH=. python examples/inspect_schema.py
    PYTHONPATH=. python examples/inspect_schema.py --stage labeled --csv examples/data/sample_labeled_dataset.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news_summarization.config import PIPELINE_STAGES
from danish_news_summarization.csv_io import read_csv
from danish_news_summarization.schema import (
    STAGE_COLUMNS,
    SchemaError,
    describe_stage,
    validate_table,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=sorted(STAGE_COLUMNS), default=None)
    parser.add_argument("--csv", type=Path, default=None)
    args = parser.parse_args()

    if args.stage:
        print(describe_stage(args.stage))
        print()
    else:
        print("Pipeline CSV contracts\n")
        for name, columns in STAGE_COLUMNS.items():
            print(f"  {name:<16} {columns}")
        print()
        print("How the original scripts line up:\n")
        for stage in PIPELINE_STAGES:
            print(f"  {stage.script:<24} {stage.input_path} → {stage.output_path}")

    if args.csv:
        if not args.stage:
            print("--csv requires --stage", file=sys.stderr)
            return 2
        rows = read_csv(args.csv)
        try:
            validate_table(args.stage, rows)
        except SchemaError as exc:
            print(f"INVALID: {exc}", file=sys.stderr)
            return 1
        print(f"OK: {args.csv} has {len(rows)} valid '{args.stage}' rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
