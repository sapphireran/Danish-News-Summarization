#!/usr/bin/env python3
"""Print length and compression statistics for a silver-label CSV.

``finetune.py`` expects ``datasets/train_dataset.csv`` with ``id,body,summary``.
The committed fixture ``examples/data/sample_labeled_danish.csv`` uses the same
schema so this script is a dry run of the checks you would want before a
multi-hour mT5 job.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news_sum.chunking import whitespace_token_count
from danish_news_sum.dataset import SILVER_COLUMNS, load_article_csv, summarize_dataset, validate_columns

DEFAULT_CSV = Path(__file__).resolve().parent / "data" / "sample_labeled_danish.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rows = load_article_csv(args.csv)
    validate_columns(rows, SILVER_COLUMNS, label=args.csv.name)
    stats = summarize_dataset(rows)

    if args.json:
        print(json.dumps(stats.as_dict(), indent=2))
        return 0

    print(f"Silver-label file: {args.csv}")
    print(f"  rows                {stats.rows}")
    print(f"  empty bodies        {stats.empty_bodies}")
    print(f"  empty summaries     {stats.empty_summaries}")
    print(f"  mean body tokens    {stats.mean_body_tokens:.1f}")
    print(f"  mean summary tokens {stats.mean_summary_tokens:.1f}")
    print(f"  mean compression    {stats.mean_compression:.2f}x")
    print(f"  mean body sentences {stats.mean_sentences:.1f}")
    print()
    print("Per-row compression")
    for row in rows:
        body_tokens = whitespace_token_count(row["body"])
        summary_tokens = whitespace_token_count(row["summary"])
        ratio = body_tokens / summary_tokens if summary_tokens else float("inf")
        print(f"  {row['id']:<24} {body_tokens:>4} -> {summary_tokens:<3}  ({ratio:4.1f}x)")
        print(f"    {row['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
