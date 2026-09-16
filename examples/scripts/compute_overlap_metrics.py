#!/usr/bin/env python3
"""Tiny ROUGE-1/2/L-style overlap scorer.

This does not load the Hugging Face ``rouge`` or ``evaluate`` packages.
There is no stemming, no bootstrap interval, and no newline sentence
trick. Use it on the synthetic fixtures or on two aligned CSV columns.

A self-overlap of a file against itself must score 1.0 on all three
averages. If it does not, the scorer is wrong.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from text_lib import mean, read_csv, score_overlap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pred", required=True, help="CSV with predictions")
    parser.add_argument("--gold", required=True, help="CSV with references")
    parser.add_argument("--pred-col", required=True)
    parser.add_argument("--gold-col", required=True)
    parser.add_argument("--id-column", default="id")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--show-rows", action="store_true", help="Print per-id scores")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pred_rows = read_csv(args.pred)
    gold_rows = read_csv(args.gold)
    if not pred_rows or not gold_rows:
        print("Both CSVs need at least one row", file=sys.stderr)
        return 1
    for label, rows, column in (
        ("pred", pred_rows, args.pred_col),
        ("gold", gold_rows, args.gold_col),
    ):
        if column not in rows[0]:
            print(f"{label} column {column!r} not in {list(rows[0])}", file=sys.stderr)
            return 2

    per_row = []
    missing = 0
    gold_index = {row.get(args.id_column, ""): row for row in gold_rows}
    for pred in pred_rows:
        key = pred.get(args.id_column, "")
        if key not in gold_index:
            missing += 1
            continue
        scores = score_overlap(pred.get(args.pred_col, ""), gold_index[key].get(args.gold_col, ""))
        item = {"id": key, **scores.as_dict()}
        per_row.append(item)

    if not per_row:
        print("No aligned ids", file=sys.stderr)
        return 1

    summary = {
        "pairs": len(per_row),
        "missing_in_gold": missing,
        "rouge1": round(mean(item["rouge1"] for item in per_row), 4),
        "rouge2": round(mean(item["rouge2"] for item in per_row), 4),
        "rougeL": round(mean(item["rougeL"] for item in per_row), 4),
        "pred": str(Path(args.pred)),
        "gold": str(Path(args.gold)),
        "pred_col": args.pred_col,
        "gold_col": args.gold_col,
    }

    if args.json:
        payload = {"summary": summary, "rows": per_row if args.show_rows else None}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"pairs:            {summary['pairs']}")
    print(f"missing in gold:  {summary['missing_in_gold']}")
    print(f"rouge1:           {summary['rouge1']:.4f}")
    print(f"rouge2:           {summary['rouge2']:.4f}")
    print(f"rougeL:           {summary['rougeL']:.4f}")
    if args.show_rows:
        print("-" * 72)
        for item in per_row:
            print(
                f"{item['id']}: r1={item['rouge1']:.3f} r2={item['rouge2']:.3f} "
                f"rL={item['rougeL']:.3f}  pred_tok={item['pred_tokens']} gold_tok={item['gold_tokens']}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
