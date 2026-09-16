#!/usr/bin/env python3
"""Print one article id through every silver-label stage.

Useful when reading the docs: you can see what `body`, `translated`,
and the two `summary` columns look like for the same story.
"""

from __future__ import annotations

import argparse
import csv
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
DATA = REPO / "examples/data"

STAGES = (
    ("1 raw Danish", DATA / "raw_articles.sample.csv", "article text"),
    ("2 English pivot", DATA / "translated_articles.sample.csv", "translated"),
    ("3 English summary", DATA / "summarized_articles.sample.csv", "summary"),
    ("4 Danish silver summary", DATA / "labeled_dataset.sample.csv", "summary"),
)


def load(path: Path, article_id: str) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["id"] == article_id:
                return row
    raise SystemExit(f"{article_id!r} not in {path}")


def wrap(text: str, width: int) -> str:
    return textwrap.fill(
        text,
        width=width,
        subsequent_indent="    ",
        initial_indent="    ",
        break_long_words=False,
        break_on_hyphens=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", default="sample-003", help="Article id to print")
    parser.add_argument("--width", type=int, default=88)
    parser.add_argument(
        "--all-ids",
        action="store_true",
        help="Print every sample id (long)",
    )
    args = parser.parse_args()

    labeled = list(csv.DictReader((DATA / "labeled_dataset.sample.csv").open(encoding="utf-8")))
    ids = [row["id"] for row in labeled] if args.all_ids else [args.id]

    for article_id in ids:
        print("=" * args.width)
        print(f"id {article_id}")
        print("=" * args.width)
        for title, path, column in STAGES:
            row = load(path, article_id)
            text = row[column]
            print(f"\n[{title}]  {path.name} :: {column}  ({len(text)} chars)")
            print(wrap(text, args.width))
        print()


if __name__ == "__main__":
    main()
