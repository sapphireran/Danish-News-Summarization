"""Score fictional model predictions with the stdlib ROUGE stand-in.

    python examples/run_rouge_demo.py
    python examples/run_rouge_demo.py --sort rougeL_f1
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.data.corpus import ARTICLES
from examples.rouge_lite import rouge_corpus, rouge_scores


def _pct(value: float) -> str:
    return f"{100 * value:5.1f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sort",
        choices=["id", "rouge1_f1", "rouge2_f1", "rougeL_f1"],
        default="id",
    )
    args = parser.parse_args()

    pairs = [(article["prediction"], article["danish_summary"]) for article in ARTICLES]
    rows, mean = rouge_corpus(pairs)

    table = []
    for article, scores in zip(ARTICLES, rows):
        table.append((article, scores))
    if args.sort != "id":
        table.sort(key=lambda item: getattr(item[1], args.sort), reverse=True)

    print("ROUGE-lite on examples/data/sample_predictions.csv")
    print("prediction = imperfect stand-in   reference = Danish silver summary")
    print("scores are F1 percentages for this tokenizer; not eval.py numbers.\n")
    print(f"{'id':<8}{'R1':>8}{'R2':>8}{'RL':>8}  preview")
    print("-" * 72)
    for article, scores in table:
        preview = article["prediction"]
        if len(preview) > 42:
            preview = preview[:39] + "..."
        print(
            f"{article['id']:<8}{_pct(scores.rouge1_f1):>8}"
            f"{_pct(scores.rouge2_f1):>8}{_pct(scores.rougeL_f1):>8}  {preview}"
        )

    print("-" * 72)
    print(
        f"{'mean':<8}{_pct(mean['rouge1_f1']):>8}"
        f"{_pct(mean['rouge2_f1']):>8}{_pct(mean['rougeL_f1']):>8}"
    )

    print("\nWorked example (da-001):")
    article = ARTICLES[0]
    detail = rouge_scores(article["prediction"], article["danish_summary"])
    print(f"  reference:  {article['danish_summary']}")
    print(f"  prediction: {article['prediction']}")
    for key, value in detail.as_dict().items():
        print(f"  {key:20s} {value:.3f}")


if __name__ == "__main__":
    main()
