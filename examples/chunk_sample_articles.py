#!/usr/bin/env python3
"""Show how the course scripts would pack the sample articles.

The original translation and summary scripts call NLTK and a model
tokenizer. This demo uses the shared helper with a whitespace-token
budget so you can see the batches without downloading weights.

Run from the repository root:

    python3 examples/chunk_sample_articles.py
    python3 examples/chunk_sample_articles.py --max-length 40
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_summarization.chunking import chunk_article, split_into_sentence_batches, text_max_length

DATA = Path(__file__).resolve().parent / "data" / "sample_articles.csv"


def load_articles(path: Path) -> list[tuple[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [(row["id"], row["article text"]) for row in csv.DictReader(handle)]


def word_count(text: str) -> int:
    return len(text.split()) + 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-length",
        type=int,
        default=80,
        help="toy token budget (course scripts use 512)",
    )
    parser.add_argument(
        "--ratio",
        type=float,
        default=0.9,
        help="safety margin used by translate.py and summary.py",
    )
    args = parser.parse_args()

    budget = text_max_length(args.max_length, args.ratio)
    print(
        f"Packing {DATA.name} with max_length={args.max_length} "
        f"ratio={args.ratio} -> budget={budget} whitespace tokens"
    )
    print()

    for article_id, body in load_articles(DATA):
        batches = split_into_sentence_batches(
            body,
            max_length=args.max_length,
            ratio=args.ratio,
            length_fn=word_count,
        )
        chunks = chunk_article(
            body,
            max_length=args.max_length,
            ratio=args.ratio,
            length_fn=word_count,
        )
        print(f"{article_id}  {word_count(body)} tokens, {len(chunks)} window(s)")
        for index, (batch, chunk) in enumerate(zip(batches, chunks), start=1):
            preview = chunk if len(chunk) < 140 else chunk[:137] + "..."
            print(f"  window {index}: {len(batch)} sentence(s), {word_count(chunk)} tokens")
            print(f"    {preview}")
        print()

    print(
        "The course scripts use Hugging Face token lengths instead of "
        "whitespace counts, so a 512-token OPUS-MT window will pack more "
        "Danish text than this toy budget."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
