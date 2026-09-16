#!/usr/bin/env python3
"""Check that the committed example CSVs still match the course contracts.

Exit status 0 means every stage file has the right columns, aligned ids,
non-empty cells, and plausible Danish / English markers.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.lib.sample_corpus import TEST_IDS, TRAIN_IDS, VALIDATION_IDS  # noqa: E402
from examples.lib.schema import (  # noqa: E402
    extra_columns,
    looks_danish,
    looks_english,
    missing_columns,
    row_is_complete,
)

DATA = Path(__file__).resolve().parent / "data"


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _fail(errors: list[str]) -> None:
    print("example data validation FAILED")
    for line in errors:
        print(f"  - {line}")
    raise SystemExit(1)


def validate(data_dir: Path = DATA) -> list[str]:
    errors: list[str] = []
    files = {
        "raw": data_dir / "raw_danish_articles.csv",
        "translated": data_dir / "translated_articles.csv",
        "summarized": data_dir / "summarized_articles.csv",
        "labeled": data_dir / "labeled_danish.csv",
        "eval": data_dir / "nordjylland_like_eval.csv",
    }
    finetune = {
        "train": data_dir / "finetune" / "train_dataset.csv",
        "validation": data_dir / "finetune" / "validation_dataset.csv",
        "test": data_dir / "finetune" / "test_dataset.csv",
    }

    for path in list(files.values()) + list(finetune.values()):
        if not path.is_file():
            errors.append(f"missing file: {path}")
    if errors:
        return errors

    tables = {name: _read(path) for name, path in files.items()}
    splits = {name: _read(path) for name, path in finetune.items()}

    stage_for_table = {
        "raw": "raw",
        "translated": "translated",
        "summarized": "summarized",
        "labeled": "labeled",
        "eval": "eval",
    }
    for name, rows in tables.items():
        stage = stage_for_table[name]
        if not rows:
            errors.append(f"{name}: file is empty")
            continue
        columns = list(rows[0].keys())
        missing = missing_columns(stage, columns)
        extra = extra_columns(stage, columns)
        if missing:
            errors.append(f"{name}: missing columns {missing}")
        if extra:
            errors.append(f"{name}: unexpected columns {extra}")
        for i, row in enumerate(rows, start=2):
            blanks = row_is_complete(row, stage)
            if blanks:
                errors.append(f"{name}: row {i} blank {blanks}")

    raw_ids = [row["id"] for row in tables["raw"]]
    if len(raw_ids) != len(set(raw_ids)):
        errors.append("raw: duplicate ids")
    for name in ("translated", "summarized", "labeled"):
        other_ids = [row["id"] for row in tables[name]]
        if other_ids != raw_ids:
            errors.append(f"{name}: id order or set does not match raw ({other_ids} vs {raw_ids})")

    raw_by_id = {row["id"]: row["article text"] for row in tables["raw"]}
    for name in ("translated", "summarized", "labeled"):
        for row in tables[name]:
            if row["body"] != raw_by_id.get(row["id"]):
                errors.append(f"{name}: body for {row['id']} drifted from raw article text")

    for row in tables["raw"]:
        if not looks_danish(row["article text"]):
            errors.append(f"raw {row['id']}: article text does not look Danish")
    for row in tables["translated"]:
        if not looks_english(row["translated"]):
            errors.append(f"translated {row['id']}: translated column looks too Danish")
        if not looks_danish(row["body"]):
            errors.append(f"translated {row['id']}: body does not look Danish")
    for row in tables["summarized"]:
        if not looks_english(row["summary"]):
            errors.append(f"summarized {row['id']}: English summary looks too Danish")
    for row in tables["labeled"]:
        if not looks_danish(row["summary"]):
            errors.append(f"labeled {row['id']}: Danish summary missing æ/ø/å")
    for i, row in enumerate(tables["eval"], start=2):
        if not looks_danish(row["input_text"]) or not looks_danish(row["target_text"]):
            errors.append(f"eval row {i}: expected Danish input_text and target_text")
        try:
            if int(row["text_len"]) <= 0 or int(row["summary_len"]) <= 0:
                errors.append(f"eval row {i}: non-positive length")
        except ValueError:
            errors.append(f"eval row {i}: lengths must be integers")

    for name, rows in splits.items():
        columns = list(rows[0].keys()) if rows else []
        if missing_columns("finetune", columns):
            errors.append(f"finetune/{name}: columns {columns}")
        if not rows:
            errors.append(f"finetune/{name}: empty")

    split_ids = {
        "train": [row["id"] for row in splits["train"]],
        "validation": [row["id"] for row in splits["validation"]],
        "test": [row["id"] for row in splits["test"]],
    }
    if split_ids["train"] != TRAIN_IDS:
        errors.append(f"train ids {split_ids['train']} != {TRAIN_IDS}")
    if split_ids["validation"] != VALIDATION_IDS:
        errors.append(f"validation ids {split_ids['validation']} != {VALIDATION_IDS}")
    if split_ids["test"] != TEST_IDS:
        errors.append(f"test ids {split_ids['test']} != {TEST_IDS}")

    combined = split_ids["train"] + split_ids["validation"] + split_ids["test"]
    if sorted(combined) != sorted(raw_ids):
        errors.append("finetune splits do not partition the raw ids")
    if len(combined) != len(set(combined)):
        errors.append("finetune splits leak ids across train/val/test")

    labeled = {row["id"]: row["summary"] for row in tables["labeled"]}
    for name, rows in splits.items():
        for row in rows:
            if row["summary"] != labeled.get(row["id"]):
                errors.append(f"finetune/{name} {row['id']}: summary mismatch vs labeled_danish.csv")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA,
        help="folder with the example CSVs (default: examples/data)",
    )
    args = parser.parse_args()
    errors = validate(args.data_dir)
    if errors:
        _fail(errors)
    n_raw = len(_read(args.data_dir / "raw_danish_articles.csv"))
    n_eval = len(_read(args.data_dir / "nordjylland_like_eval.csv"))
    print("example data validation OK")
    print(f"  articles: {n_raw}")
    print(f"  eval rows: {n_eval}")
    print(f"  splits: {len(TRAIN_IDS)}/{len(VALIDATION_IDS)}/{len(TEST_IDS)} train/val/test")


if __name__ == "__main__":
    main()
