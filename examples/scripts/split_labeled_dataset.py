#!/usr/bin/env python3
"""Split a labeled CSV into the three files finetune.py expects.

The 2023 repository never committed this stage. Splits are by unique id,
not by row, so a duplicated id cannot land in two buckets.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from text_lib import read_csv, split_rows, write_csv

SPLIT_NAMES = ("train", "validation", "test")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="labeled CSV with id, body, summary")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--train", type=float, default=0.9)
    parser.add_argument("--validation", type=float, default=0.05)
    parser.add_argument("--test", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=2023)
    parser.add_argument("--id-column", default="id")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = read_csv(args.input)
    if not rows:
        print("No rows to split", file=sys.stderr)
        return 1
    required = {"id", "body", "summary"}
    missing = required.difference(rows[0])
    if missing:
        print(f"Input is missing columns: {sorted(missing)}", file=sys.stderr)
        return 2

    try:
        buckets = split_rows(
            rows,
            train=args.train,
            validation=args.validation,
            test=args.test,
            seed=args.seed,
            id_column=args.id_column,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir)
    written = {}
    for name in SPLIT_NAMES:
        destination = output_dir / f"{name}_dataset.csv"
        write_csv(destination, buckets[name], ("id", "body", "summary"))
        written[name] = {"path": str(destination), "rows": len(buckets[name])}

    # Guard against id leakage.
    seen: dict[str, str] = {}
    leaks = []
    for name in SPLIT_NAMES:
        for row in buckets[name]:
            key = row["id"]
            if key in seen:
                leaks.append(f"{key} in {seen[key]} and {name}")
            else:
                seen[key] = name

    summary = {
        "input": args.input,
        "seed": args.seed,
        "ratios": {
            "train": args.train,
            "validation": args.validation,
            "test": args.test,
        },
        "splits": written,
        "leaks": leaks,
    }

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        for name in SPLIT_NAMES:
            info = written[name]
            print(f"{name:12} {info['rows']:4d}  {info['path']}")
        if leaks:
            print("id leaks:")
            for leak in leaks:
                print(f"  - {leak}")
    return 1 if leaks else 0


if __name__ == "__main__":
    sys.exit(main())
