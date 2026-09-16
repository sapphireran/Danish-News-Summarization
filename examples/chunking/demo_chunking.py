#!/usr/bin/env python3
"""Show how sample-010 (the long port plan) is packed.

Uses WhitespaceApproxTokenizer by default so the demo runs with the
stdlib only. Pass --limit to pretend you are Marian (460) or T5 (512).
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from article_chunker import (  # noqa: E402
    WhitespaceApproxTokenizer,
    report_pack,
    split_long_sentence,
)


def load_article(csv_path: Path, article_id: str, column: str) -> str:
    with csv_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["id"] == article_id:
                return row[column]
    raise SystemExit(f"id {article_id!r} not found in {csv_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        type=Path,
        default=REPO / "examples/data/translated_articles.sample.csv",
        help="CSV with an id column and the text column",
    )
    parser.add_argument("--id", default="sample-010", help="Article id to pack")
    parser.add_argument(
        "--column",
        default="translated",
        help="Text column (translated, body, or 'article text')",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=80,
        help="Pack budget in approximate tokens (default 80 so the sample splits)",
    )
    parser.add_argument(
        "--no-split-overlong",
        action="store_true",
        help="Match translate_back.py and skip the character splitter",
    )
    parser.add_argument(
        "--demo-long-sentence",
        action="store_true",
        help="Also run split_long_sentence on a one-line run-on",
    )
    args = parser.parse_args()

    article = load_article(args.csv, args.id, args.column)
    report = report_pack(
        article,
        args.limit,
        WhitespaceApproxTokenizer(),
        split_overlong=not args.no_split_overlong,
    )

    print(f"id:                 {args.id}")
    print(f"column:             {args.column}")
    print(f"pack limit:         {args.limit} approx tokens")
    print(f"article chars:      {report.article_chars}")
    print(f"article ~tokens:    {report.article_approx_tokens}")
    print(f"source sentences:   {report.n_source_sentences}")
    print(f"packed chunks:      {report.n_chunks}")
    print(f"chunk ~tokens:      {report.chunk_token_lengths}")
    print(f"chunk chars:        {report.chunk_char_lengths}")
    print()
    for i, chunk in enumerate(report.chunks, start=1):
        preview = chunk if len(chunk) <= 220 else chunk[:217] + "..."
        print(f"--- chunk {i}/{report.n_chunks} ---")
        print(preview)
        print()

    over_budget = [
        length for length in report.chunk_token_lengths if length > args.limit
    ]
    if over_budget:
        raise SystemExit(f"packer failed: chunks over limit {over_budget}")

    if args.demo_long_sentence:
        run_on = (
            "The quay is lorries, empty sheds, a fence with three holes, a rusty "
            "crane without a certificate, three fish auctions before dawn, and a "
            "tent hall that has already survived three budgets that promised it "
            "something permanent, according to residents who collected signatures."
        )
        pieces = split_long_sentence(run_on, max_length=60)
        print("split_long_sentence demo (char budget 60):")
        for i, piece in enumerate(pieces, start=1):
            print(f"  {i}. ({len(piece):3d} chars) {piece}")

    print("ok")


if __name__ == "__main__":
    main()
