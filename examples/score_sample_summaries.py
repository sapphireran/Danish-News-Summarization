#!/usr/bin/env python3
"""Score committed prediction/reference pairs with offline lexical metrics.

This is not a replacement for ``eval.py``. It exists so the evaluation *shape*
(ROUGE-1 / ROUGE-2 / ROUGE-L style F1, plus compression) can be demonstrated
without downloading mT5, XLM-R, or the Nordjylland News dataset.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news_sum.dataset import EVAL_COLUMNS, load_article_csv, validate_columns
from danish_news_sum.metrics import aggregate_scores, lexical_scores

DEFAULT_CSV = Path(__file__).resolve().parent / "data" / "sample_eval_pairs.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rows = load_article_csv(args.csv)
    validate_columns(rows, EVAL_COLUMNS, label=args.csv.name)
    scored = [
        {
            "id": row["id"],
            **lexical_scores(
                prediction=row["prediction"],
                reference=row["target_text"],
                article=row["input_text"],
            ),
        }
        for row in rows
    ]
    numeric = [{key: value for key, value in row.items() if key != "id"} for row in scored]
    summary = aggregate_scores(numeric)

    if args.json:
        print(json.dumps({"pairs": scored, "mean": summary}, ensure_ascii=False, indent=2))
        return 0

    print(f"Lexical scores for {len(scored)} pairs in {args.csv.name}")
    print()
    print(f"{'id':<24} {'R1':>6} {'R2':>6} {'RL':>6} {'comp':>6}")
    for row in scored:
        print(
            f"{row['id']:<24} "
            f"{row['rouge1_f1']:6.3f} "
            f"{row['rouge2_f1']:6.3f} "
            f"{row['rougeL_f1']:6.3f} "
            f"{row['compression_ratio']:6.2f}"
        )
    print("-" * 52)
    print(
        f"{'mean':<24} "
        f"{summary['rouge1_f1']:6.3f} "
        f"{summary['rouge2_f1']:6.3f} "
        f"{summary['rougeL_f1']:6.3f} "
        f"{summary['compression_ratio']:6.2f}"
    )
    print()
    print("These are overlap F1 scores on word tokens, not Hugging Face rouge / bertscore.")
    print("Use eval.py when a fine-tuned checkpoint and GPU time are available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
