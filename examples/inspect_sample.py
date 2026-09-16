"""Print one sample article through every CSV stage, or validate a folder."""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path
from typing import Dict, Sequence

from examples.schemas import (
    STAGE_COLUMNS,
    SchemaError,
    read_csv,
    validate_csv,
    validate_sample_dir,
)
from examples.text_chunking import iter_chunk_report

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"
STAGE_FILES = (
    ("raw", "00_raw_articles.csv"),
    ("translated", "01_translated_articles.csv"),
    ("summarized", "02_summarized_articles.csv"),
    ("labeled", "03_labeled_dataset.csv"),
)


def _wrap(title: str, body: str) -> None:
    print(title)
    print(textwrap.indent(textwrap.fill(body, width=88), "    "))
    print()


def load_indexed(directory: Path) -> Dict[str, Dict[str, Dict[str, str]]]:
    """Return ``{stage: {id: row}}`` for the four main sample files."""
    indexed: Dict[str, Dict[str, Dict[str, str]]] = {}
    for stage, name in STAGE_FILES:
        rows = validate_csv(directory / name, STAGE_COLUMNS[stage], stage=stage)
        indexed[stage] = {row["id"]: row for row in rows}
    return indexed


def print_article(directory: Path, article_id: str, budget: int) -> None:
    indexed = load_indexed(directory)
    if article_id not in indexed["raw"]:
        known = ", ".join(sorted(indexed["raw"]))
        raise SchemaError(f"unknown id {article_id!r}; known ids: {known}")

    print(f"Article id: {article_id}")
    print(f"Sample dir: {directory}")
    print()

    raw = indexed["raw"][article_id]
    _wrap("Raw Danish (article text)", raw["article text"])
    _wrap("Translated English (fixture)", indexed["translated"][article_id]["translated"])
    _wrap("English summary (fixture)", indexed["summarized"][article_id]["summary"])
    _wrap("Danish silver summary (fixture)", indexed["labeled"][article_id]["summary"])

    print(f"Chunk report for the Danish body (budget={budget}, default word estimator):")
    for item in iter_chunk_report(raw["article text"], budget):
        flag = "ok" if item["fits"] else "OVER"
        print(f"  [{item['index']}] {item['length']}/{item['budget']} {flag}")
        print(textwrap.indent(textwrap.fill(item["text"], width=84), "      "))


def list_ids(directory: Path) -> None:
    rows = read_csv(directory / "00_raw_articles.csv")
    print("Sample article ids:")
    for row in rows:
        preview = row["article text"].split(".")[0][:70]
        print(f"  {row['id']:28}  {preview}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, default=SAMPLE_DIR)
    parser.add_argument("--article-id", help="Print every stage for this id")
    parser.add_argument("--list-ids", action="store_true", help="List sample ids and exit")
    parser.add_argument(
        "--validate-dir",
        type=Path,
        help="Validate a directory of sample-style CSVs and print row counts",
    )
    parser.add_argument("--budget", type=int, default=460, help="Packing budget for the chunk report")
    args = parser.parse_args(argv)

    try:
        if args.validate_dir is not None:
            counts = validate_sample_dir(args.validate_dir)
            for name, count in sorted(counts.items()):
                print(f"{name}: {count} row(s)")
            return 0
        if args.list_ids:
            list_ids(args.sample_dir)
            return 0
        if args.article_id:
            print_article(args.sample_dir, args.article_id, args.budget)
            return 0
        list_ids(args.sample_dir)
        print()
        print("Pass --article-id <id> to print the full stage walkthrough.")
        return 0
    except SchemaError as error:
        print(f"schema error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
