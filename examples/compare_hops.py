#!/usr/bin/env python3
"""Compare silver Danish summaries to the source article and a lead-1 baseline.

This is a teaching table, not an evaluation of mT5. Overlap is computed
with the tiny ROUGE stand-in in `dns_examples.metrics`.

    python examples/compare_hops.py
    python examples/compare_hops.py --id oesterhavn-kvote
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

from dns_examples.io import read_csv  # noqa: E402
from dns_examples.metrics import summarize_pair  # noqa: E402
from dns_examples.mock_models import lead_n_danish  # noqa: E402
from dns_examples.paths import DATA_DIR  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--id", dest="only_id", default=None, help="Restrict to one slug")
    parser.add_argument("--lead", type=int, default=1, help="Lead-N extractive baseline")
    return parser


def _line(row_id: str, tag: str, scores) -> str:
    return (
        f"{row_id:24} {tag:8} "
        f"R1={scores.rouge1_f:5.2f} R2={scores.rouge2_f:5.2f} "
        f"RL={scores.rougeL_f:5.2f} comp={scores.compression:4.2f}"
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    labeled = read_csv(args.data_dir / "sample_labeled.csv")
    if args.only_id:
        labeled = [row for row in labeled if row["id"] == args.only_id]
        if not labeled:
            print(f"unknown id {args.only_id}", file=sys.stderr)
            return 2

    print("Overlap of a candidate Danish summary against the Danish article.")
    print("silver = hand-written stand-in for translate_back.py")
    print(f"lead{args.lead}  = first {args.lead} sentence(s) of the article")
    print()
    for row in labeled:
        silver = summarize_pair(row["id"], row["body"], row["summary"])
        lead = lead_n_danish(row["body"], args.lead)
        lead_scores = summarize_pair(row["id"], row["body"], lead)
        print(_line(row["id"], "silver", silver))
        print(_line(row["id"], f"lead{args.lead}", lead_scores))
        if args.only_id:
            print()
            print("article:")
            print(f"  {row['body']}")
            print("silver:")
            print(f"  {row['summary']}")
            print(f"lead{args.lead}:")
            print(f"  {lead}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
