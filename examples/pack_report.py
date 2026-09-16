#!/usr/bin/env python3
"""Show how the 2023 packer would cut each fictional article.

    python examples/pack_report.py
    python examples/pack_report.py --budget 20 --id oesterhavn-kvote
    python examples/pack_report.py --budgets 20,40,80
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

from dns_examples.chunking import WhitespaceCounter, groups_to_text, split_into_sentence_groups  # noqa: E402
from dns_examples.io import read_csv  # noqa: E402
from dns_examples.paths import DATA_DIR  # noqa: E402
from dns_examples.sentences import split_sentences  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--articles", type=Path, default=DATA_DIR / "sample_articles.csv")
    parser.add_argument("--id", dest="only_id", default=None)
    parser.add_argument("--budget", type=int, default=None, help="Single whitespace-token budget")
    parser.add_argument(
        "--budgets",
        default="20,40,80",
        help="Comma-separated budgets (ignored if --budget is set)",
    )
    parser.add_argument(
        "--no-split-oversized",
        action="store_true",
        help="Disable the comma/semicolon long-sentence breaker",
    )
    return parser


def _budgets(args: argparse.Namespace) -> list[int]:
    if args.budget is not None:
        return [args.budget]
    return [int(part.strip()) for part in args.budgets.split(",") if part.strip()]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = read_csv(args.articles)
    if args.only_id:
        rows = [row for row in rows if row["id"] == args.only_id]
        if not rows:
            print(f"unknown id {args.only_id}", file=sys.stderr)
            return 2

    counter = WhitespaceCounter()
    budgets = _budgets(args)
    print(
        "Packer matches translate.py / summary.py: sentence split, optional "
        "comma-break on oversized sentences, then greedy groups."
    )
    print("Counter is whitespace words + 2 specials, not Marian subwords.")
    print()

    for row in rows:
        danish = row["article text"]
        sentences = split_sentences(danish)
        print(f"## {row['id']}  ({len(sentences)} sentence(s), {counter.count(danish)} white-tokens)")
        for budget in budgets:
            groups = split_into_sentence_groups(
                danish,
                budget,
                counter,
                split_oversized=not args.no_split_oversized,
            )
            texts = groups_to_text(groups)
            print(f"  budget {budget:3d} → {len(groups)} group(s)")
            for index, text in enumerate(texts, start=1):
                preview = text if len(text) <= 160 else text[:157] + "..."
                print(f"    [{index}] ({counter.count(text):3d}) {preview}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
