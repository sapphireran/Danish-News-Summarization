#!/usr/bin/env python3
"""Compare extractive silver labels with the hand-written gold summaries.

The course evaluation uses ROUGE and BERTScore against Nordjylland news.
Those metrics need model downloads. This script stays offline and reports
unigram overlap on Danish content words so you can see how a cheap
extractive baseline differs from the curated gold files.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from examples.extractive_summary import content_tokens, extractive_summarize


def unigram_f1(prediction: str, reference: str) -> dict[str, float]:
    pred = content_tokens(prediction)
    ref = content_tokens(reference)
    pred_set = set(pred)
    ref_set = set(ref)
    if not pred_set and not ref_set:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not pred_set or not ref_set:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    overlap = pred_set & ref_set
    precision = len(overlap) / len(pred_set)
    recall = len(overlap) / len(ref_set)
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


def load_labeled(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["id"]: row["summary"] for row in csv.DictReader(handle)}


def compare(
    gold_path: Path,
    silver_path: Path | None,
    max_sentences: int,
    max_chars: int,
) -> dict[str, object]:
    gold = load_labeled(gold_path)
    if silver_path is not None:
        silver = load_labeled(silver_path)
    else:
        # Recompute extractive summaries from the gold file bodies.
        with gold_path.open(newline="", encoding="utf-8") as handle:
            silver = {
                row["id"]: extractive_summarize(
                    row["body"],
                    max_sentences=max_sentences,
                    max_chars=max_chars,
                )
                for row in csv.DictReader(handle)
            }

    rows = []
    for article_id, reference in gold.items():
        if article_id not in silver:
            raise KeyError(f"{article_id} missing from silver labels")
        scores = unigram_f1(silver[article_id], reference)
        rows.append(
            {
                "id": article_id,
                "precision": round(scores["precision"], 4),
                "recall": round(scores["recall"], 4),
                "f1": round(scores["f1"], 4),
                "silver": silver[article_id],
                "gold": reference,
            }
        )

    mean_f1 = sum(row["f1"] for row in rows) / len(rows)
    return {"pairs": rows, "mean_content_f1": round(mean_f1, 4), "n": len(rows)}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gold",
        type=Path,
        default=_ROOT / "examples" / "data" / "sample_labeled.csv",
    )
    parser.add_argument(
        "--silver",
        type=Path,
        help="Optional labeled CSV to compare. Default: recompute extractive summaries.",
    )
    parser.add_argument("--max-summary-sentences", type=int, default=2)
    parser.add_argument("--max-summary-chars", type=int, default=320)
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a table.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = compare(
        gold_path=args.gold,
        silver_path=args.silver,
        max_sentences=args.max_summary_sentences,
        max_chars=args.max_summary_chars,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print("Content-word overlap versus gold summaries")
    print("=========================================")
    print(f"{'id':<22} {'P':>6} {'R':>6} {'F1':>6}")
    for row in report["pairs"]:
        print(f"{row['id']:<22} {row['precision']:>6.3f} {row['recall']:>6.3f} {row['f1']:>6.3f}")
    print(f"\nmean F1 over {report['n']} articles: {report['mean_content_f1']:.3f}")
    print("This is not ROUGE or BERTScore; see docs/evaluation.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
