#!/usr/bin/env python3
"""Print character-length stats for every sample CSV.

Tokenizers are intentionally not loaded. This is a shape check you can
run on a laptop before kicking off CTranslate2.
"""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

FILES = (
    ("raw_articles.sample.csv", ("article text",)),
    ("translated_articles.sample.csv", ("body", "translated")),
    ("summarized_articles.sample.csv", ("body", "translated", "summary")),
    ("labeled_dataset.sample.csv", ("body", "summary")),
    ("train_dataset.sample.csv", ("body", "summary")),
    ("validation_dataset.sample.csv", ("body", "summary")),
    ("test_dataset.sample.csv", ("body", "summary")),
)


def _stats(values: list[int]) -> str:
    if not values:
        return "n=0"
    return (
        f"n={len(values)}  min={min(values)}  max={max(values)}  "
        f"mean={statistics.mean(values):.0f}  median={statistics.median(values):.0f}"
    )


def inspect(path: Path, columns: tuple[str, ...]) -> None:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    print(f"## {path.name}  ({len(rows)} rows)")
    print(f"   columns: {list(rows[0].keys()) if rows else []}")
    for col in columns:
        lengths = [len(row[col]) for row in rows]
        print(f"   {col!r:16s}  chars {_stats(lengths)}")
        if col == "summary" and "body" in rows[0]:
            ratios = [
                len(row["summary"]) / max(len(row["body"]), 1) for row in rows
            ]
            print(
                f"   {'summary/body':16s}  ratio "
                f"min={min(ratios):.3f}  max={max(ratios):.3f}  "
                f"mean={statistics.mean(ratios):.3f}"
            )
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=REPO / "examples/data",
    )
    args = parser.parse_args()
    for name, columns in FILES:
        path = args.data_dir / name
        if not path.is_file():
            print(f"## {name}  MISSING")
            continue
        inspect(path, columns)


if __name__ == "__main__":
    main()
