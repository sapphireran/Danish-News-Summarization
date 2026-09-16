#!/usr/bin/env python3
"""Print a compact inventory of the curated example CSVs."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from examples.danish_sentences import split_danish_sentences  # noqa: E402
from examples.schema import PIPELINE_SCHEMAS  # noqa: E402
from examples.text_chunking import word_length  # noqa: E402

STAGE_FILES = (
    ("raw_articles", "sample_articles.csv", "article text"),
    ("translated_articles", "sample_translated.csv", "translated"),
    ("summarized_english", "sample_summarized.csv", "summary"),
    ("labeled_danish", "sample_labeled.csv", "summary"),
)


def describe(path: Path, text_column: str) -> str:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return f"{path.name}: empty"
    lengths = [word_length(row[text_column]) for row in rows]
    sent_counts = [len(split_danish_sentences(row[text_column])) for row in rows]
    ids = ", ".join(row["id"] for row in rows)
    return (
        f"{path.name}: {len(rows)} rows  "
        f"ids=[{ids}]  "
        f"words={min(lengths)}-{max(lengths)}  "
        f"sentences={min(sent_counts)}-{max(sent_counts)}"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "data",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    print("Example dataset inventory")
    print("=========================")
    for stage, filename, column in STAGE_FILES:
        path = args.data_dir / filename
        schema = PIPELINE_SCHEMAS[stage]
        print(f"\n[{stage}] produced conceptually by {schema.produced_by}")
        print(f"  columns: {', '.join(schema.required_names)}")
        print(f"  {describe(path, column)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
