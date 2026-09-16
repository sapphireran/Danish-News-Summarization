#!/usr/bin/env python3
"""Validate every checked-in sample CSV against the pipeline schemas."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from schema import (  # noqa: E402
    STAGE_COLUMNS,
    disjoint_ids,
    read_rows,
    validate_file,
)

SAMPLES = (
    ("raw_articles.sample.csv", "raw"),
    ("translated_articles.sample.csv", "translated"),
    ("summarized_articles.sample.csv", "summarized"),
    ("labeled_dataset.sample.csv", "labeled"),
    ("train_dataset.sample.csv", "labeled"),
    ("validation_dataset.sample.csv", "labeled"),
    ("test_dataset.sample.csv", "labeled"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=REPO / "examples/data",
        help="Directory with *.sample.csv files",
    )
    args = parser.parse_args()

    results = []
    failed = False
    for name, stage in SAMPLES:
        path = args.data_dir / name
        if not path.is_file():
            print(f"[FAIL] missing {path}")
            failed = True
            continue
        result = validate_file(path, stage)
        results.append(result)
        print("\n".join(result.lines()))
        failed = failed or not result.ok

    # Cross-file: splits must be disjoint and cover the labeled set.
    labeled_path = args.data_dir / "labeled_dataset.sample.csv"
    split_names = (
        "train_dataset.sample.csv",
        "validation_dataset.sample.csv",
        "test_dataset.sample.csv",
    )
    if labeled_path.is_file() and all((args.data_dir / n).is_file() for n in split_names):
        _, labeled_rows = read_rows(labeled_path)
        parts = []
        split_ids: set[str] = set()
        for name in split_names:
            _, rows = read_rows(args.data_dir / name)
            parts.append((name, rows))
            split_ids.update(row["id"] for row in rows)
        overlap = disjoint_ids(parts)
        labeled_ids = {row["id"] for row in labeled_rows}
        missing = sorted(labeled_ids - split_ids)
        extra = sorted(split_ids - labeled_ids)
        if overlap or missing or extra:
            failed = True
            print("[FAIL] split coverage")
            for item in overlap:
                print(f"  error: {item}")
            if missing:
                print(f"  error: labeled ids missing from splits: {missing}")
            if extra:
                print(f"  error: split ids not in labeled file: {extra}")
        else:
            print(
                f"[OK] splits are disjoint and cover {len(labeled_ids)} labeled ids"
            )

        # Stage-to-stage id alignment for the four full-corpus files.
        full = (
            "raw_articles.sample.csv",
            "translated_articles.sample.csv",
            "summarized_articles.sample.csv",
            "labeled_dataset.sample.csv",
        )
        id_sets = []
        for name in full:
            _, rows = read_rows(args.data_dir / name)
            id_sets.append((name, [row["id"] for row in rows]))
        first_name, first_ids = id_sets[0]
        for name, ids in id_sets[1:]:
            if ids != first_ids:
                failed = True
                print(
                    f"[FAIL] id order/membership {name} != {first_name}: "
                    f"{ids} vs {first_ids}"
                )
        if all(ids == first_ids for _, ids in id_sets[1:]):
            print(f"[OK] stage files share id order with {first_name}")

    print(f"known stages: {sorted(STAGE_COLUMNS)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
