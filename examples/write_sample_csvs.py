#!/usr/bin/env python3
"""Write the curated example CSVs from ``sample_catalog.py``."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from examples.sample_catalog import SAMPLES


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def build_rows() -> dict[str, list[dict[str, str]]]:
    raw = [{"id": row["id"], "article text": row["body_da"]} for row in SAMPLES]
    translated = [
        {"id": row["id"], "body": row["body_da"], "translated": row["body_en"]}
        for row in SAMPLES
    ]
    summarized = [
        {
            "id": row["id"],
            "body": row["body_da"],
            "translated": row["body_en"],
            "summary": row["summary_en"],
        }
        for row in SAMPLES
    ]
    labeled = [
        {"id": row["id"], "body": row["body_da"], "summary": row["summary_da"]}
        for row in SAMPLES
    ]

    splits: dict[str, list[dict[str, str]]] = {"train": [], "validation": [], "test": []}
    for row in SAMPLES:
        splits[row["split"]].append(
            {"id": row["id"], "body": row["body_da"], "summary": row["summary_da"]}
        )

    return {
        "sample_articles.csv": raw,
        "sample_translated.csv": translated,
        "sample_summarized.csv": summarized,
        "sample_labeled.csv": labeled,
        "sample_finetune_train.csv": splits["train"],
        "sample_finetune_validation.csv": splits["validation"],
        "sample_finetune_test.csv": splits["test"],
    }


COLUMNS = {
    "sample_articles.csv": ["id", "article text"],
    "sample_translated.csv": ["id", "body", "translated"],
    "sample_summarized.csv": ["id", "body", "translated", "summary"],
    "sample_labeled.csv": ["id", "body", "summary"],
    "sample_finetune_train.csv": ["id", "body", "summary"],
    "sample_finetune_validation.csv": ["id", "body", "summary"],
    "sample_finetune_test.csv": ["id", "body", "summary"],
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "data",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    tables = build_rows()
    for filename, rows in tables.items():
        path = args.output_dir / filename
        write_csv(path, COLUMNS[filename], rows)
        print(f"wrote {path} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
