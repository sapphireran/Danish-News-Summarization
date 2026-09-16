#!/usr/bin/env python3
"""Show how articles are packed into model-sized batches.

The course translation scripts never send a whole newspaper article to
OPUS-MT at once. They sentence-split, break leftover long sentences, then
pack the pieces so the running token budget stays under 90% of 512.

This demo uses word counts instead of a SentencePiece tokenizer so it can
run offline. Use ``--max-length`` to pretend you have a tiny model; the
sample harbor article will then spill across several batches.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from examples.text_chunking import (  # noqa: E402
    flatten_batches,
    split_into_sentence_batches,
    word_length,
)


def load_articles(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def render_article(row: dict[str, str], max_length: int, mode: str) -> str:
    article = row["article text"]
    batches = split_into_sentence_batches(article, max_length=max_length, mode=mode)
    lines = [
        f"id={row['id']}",
        f"words={word_length(article)}  sentences_or_chunks={sum(len(batch) for batch in batches)}  batches={len(batches)}",
        f"mode={mode}  max_length={max_length} (word units)",
    ]
    for index, batch in enumerate(batches, start=1):
        joined = flatten_batches([batch])[0]
        preview = joined if len(joined) <= 160 else joined[:157] + "..."
        lines.append(f"  batch {index:02d}  units={len(batch):2d}  words={word_length(joined):3d}  {preview}")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parent / "data" / "sample_articles.csv",
    )
    parser.add_argument("--max-length", type=int, default=40, help="Word budget per batch.")
    parser.add_argument(
        "--mode",
        choices=("near_limit", "historical"),
        default="near_limit",
    )
    parser.add_argument("--id", dest="article_id", help="Only show this article id.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rows = load_articles(args.input)
    if args.article_id:
        rows = [row for row in rows if row["id"] == args.article_id]
        if not rows:
            print(f"error: no article with id {args.article_id!r}", file=sys.stderr)
            return 1

    blocks = [render_article(row, args.max_length, args.mode) for row in rows]
    print("\n\n".join(blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
