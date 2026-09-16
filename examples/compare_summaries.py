"""Print Danish body, silver label, and stand-in prediction side by side.

    python examples/compare_summaries.py
    python examples/compare_summaries.py --id da-010
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.data.corpus import ARTICLES, articles_by_id
from examples.rouge_lite import rouge_scores


def compare(article_id: str) -> None:
    article = articles_by_id()[article_id]
    scores = rouge_scores(article["prediction"], article["danish_summary"])
    print(f"{article_id}  split={article['split']}")
    print("\nBODY (Danish, truncated to 500 chars)")
    body = article["danish_body"]
    print(body if len(body) <= 500 else body[:497] + "...")
    print("\nREFERENCE  (Danish silver label, as if from translate_back.py)")
    print(article["danish_summary"])
    print("\nPREDICTION (fictional model output for the ROUGE demo)")
    print(article["prediction"])
    print(
        "\nROUGE-lite F1   "
        f"R1={scores.rouge1_f1:.3f}  R2={scores.rouge2_f1:.3f}  "
        f"RL={scores.rougeL_f1:.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", dest="article_id", default=None)
    args = parser.parse_args()
    ids = [args.article_id] if args.article_id else [article["id"] for article in ARTICLES]
    for index, article_id in enumerate(ids):
        if article_id not in articles_by_id():
            raise SystemExit(f"unknown id {article_id}")
        if index:
            print("\n" + "#" * 72 + "\n")
        compare(article_id)


if __name__ == "__main__":
    main()
