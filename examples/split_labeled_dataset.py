#!/usr/bin/env python3
"""Split a labeled CSV into the three files finetune.py expects.

The course repository never included a splitter. This one is deterministic:
rows are sorted by id, then assigned with a seeded shuffle so reruns match.

    python3 examples/split_labeled_dataset.py \\
        --input examples/sample_data/03_labeled_sample.csv \\
        --output-dir /tmp/dns-splits \\
        --train-ratio 0.8 --val-ratio 0.1

Default output names: train_dataset.csv, validation_dataset.csv,
test_dataset.csv. Pass --sample-names to write the 04_* filenames used
under examples/sample_data/.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from csv_util import read_rows, write_rows
from schema import FINETUNE_SPLIT_FILENAMES, SPLIT_FILENAMES, required_columns
from validate_csvs import validate_file

STAGE = "labeled"
SPLIT_STAGE = "split"


def split_rows(
    rows: list[dict[str, str]],
    train_ratio: float,
    val_ratio: float,
    seed: int,
) -> dict[str, list[dict[str, str]]]:
    if train_ratio <= 0 or val_ratio < 0:
        raise ValueError("train_ratio must be > 0 and val_ratio must be >= 0")
    if train_ratio + val_ratio >= 1:
        raise ValueError("train_ratio + val_ratio must be < 1 (remainder is test)")
    if not rows:
        raise ValueError("no rows to split")

    ordered = sorted(rows, key=lambda row: row.get("id", ""))
    rng = random.Random(seed)
    rng.shuffle(ordered)

    n_rows = len(ordered)
    n_train = int(n_rows * train_ratio)
    n_val = int(n_rows * val_ratio)
    # Give leftover rows to test, but keep at least one train row.
    n_train = max(1, n_train)
    if n_train >= n_rows:
        raise ValueError("not enough rows for a train split")
    remaining = n_rows - n_train
    if remaining == 0:
        raise ValueError("not enough rows to leave a validation/test remainder")
    n_val = min(n_val, remaining)
    # Prefer a non-empty test set when there are leftover rows after val.
    if remaining - n_val == 0 and remaining > 1 and n_val > 0:
        n_val -= 1

    train = ordered[:n_train]
    validation = ordered[n_train : n_train + n_val]
    test = ordered[n_train + n_val :]
    if not test:
        # Steal the last validation row if we would otherwise drop the test file.
        if validation:
            test = [validation.pop()]
        else:
            test = [train.pop()]
            if not train:
                raise ValueError("need at least two rows to create train and test")

    return {"train": train, "validation": validation, "test": test}


def write_splits(
    input_path: Path,
    output_dir: Path,
    train_ratio: float,
    val_ratio: float,
    seed: int,
    sample_names: bool,
) -> dict[str, Path]:
    header, rows = read_rows(input_path)
    missing = [column for column in required_columns(STAGE) if column not in header]
    if missing:
        raise ValueError(f"{input_path} is missing columns {missing}")

    issues = validate_file(input_path, STAGE)
    hard = [issue for issue in issues if issue.kind in {"columns", "duplicate_id", "empty_id"}]
    if hard:
        raise ValueError("; ".join(str(issue) for issue in hard))

    split = split_rows(rows, train_ratio=train_ratio, val_ratio=val_ratio, seed=seed)
    names = SPLIT_FILENAMES if sample_names else FINETUNE_SPLIT_FILENAMES
    written: dict[str, Path] = {}
    out_header = list(required_columns(SPLIT_STAGE))
    for name, filename in names.items():
        path = output_dir / filename
        write_rows(path, out_header, split[name])
        written[name] = path
    return written


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=2023)
    parser.add_argument(
        "--sample-names",
        action="store_true",
        help="write 04_*_split_sample.csv names instead of finetune.py names",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    written = write_splits(
        input_path=args.input,
        output_dir=args.output_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        seed=args.seed,
        sample_names=args.sample_names,
    )
    for name, path in written.items():
        _, rows = read_rows(path)
        print(f"{name:12} {len(rows):4}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
