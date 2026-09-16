#!/usr/bin/env python3
"""Compare packing budgets the way the 2023 scripts chose them.

translate.py uses ``int(512 * 0.9)`` so a 512-token model never sits
exactly on the edge. summary.py uses 512 for packing and 80 for the
generated summary. This script shows, for each sample article, how many
windows you get at a few budgets — a cheap way to guess GPU time.

    PYTHONPATH=. python examples/compare_chunk_strategies.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news_summarization.chunking import WhitespaceTokenizer, split_article
from danish_news_summarization.sample_data import SAMPLE_ARTICLES

BUDGETS = (24, 40, 80, 120, 200)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--budgets",
        type=int,
        nargs="+",
        default=list(BUDGETS),
        help="Whitespace-token budgets to compare (default: %(default)s).",
    )
    args = parser.parse_args()

    tokenizer = WhitespaceTokenizer()
    header = f"{'id':<8} {'words':>6}" + "".join(f"  b={b:<4}" for b in args.budgets)
    print(header)
    print("-" * len(header))

    totals = {budget: 0 for budget in args.budgets}
    for article in SAMPLE_ARTICLES:
        words = len(article.body.split())
        counts = []
        for budget in args.budgets:
            n = len(split_article(article.body, budget, tokenizer))
            totals[budget] += n
            counts.append(n)
        cells = "".join(f"{count:>8}" for count in counts)
        print(f"{article.id:<8} {words:>6}{cells}")

    print("-" * len(header))
    total_cells = "".join(f"{totals[budget]:>8}" for budget in args.budgets)
    print(f"{'Σ windows':<8} {'':>6}{total_cells}")
    print()
    print("Reading the table")
    print("  • Each extra window is another translator / summarizer call.")
    print("  • The original OPUS-MT scripts pack at 460 subword tokens, not whitespace.")
    print("  • Danish compounds tokenize to more subwords than these word counts suggest.")
    print("  • summary.py's generate() max_length=80 is independent of the pack budget.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
