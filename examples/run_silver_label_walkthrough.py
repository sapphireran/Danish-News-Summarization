"""Walk one article through the silver-label column transforms.

The 2023 scripts need converted OPUS models and an English T5. This
walkthrough uses the pre-written fictional translations and summaries
so you can see the *table shape* of each stage without a GPU.

    python examples/run_silver_label_walkthrough.py
    python examples/run_silver_label_walkthrough.py --id da-006
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.data.corpus import ARTICLES, articles_by_id
from examples.danish_sentences import word_tokenize


def _block(title: str, text: str) -> None:
    print(f"\n--- {title} ---")
    print(text)


def _counts(label: str, text: str) -> None:
    print(f"    ({label}: {len(text)} chars, {len(word_tokenize(text))} words)")


def walk(article_id: str) -> None:
    article = articles_by_id()[article_id]
    print(f"Silver-label walkthrough for {article_id} (split={article['split']})")
    print("All strings below are fictional documentation text, not model output.")

    print("\n[1] translate.py input   columns: id, article text")
    _block("article text (Danish)", article["danish_body"])
    _counts("body", article["danish_body"])

    print("\n[2] translate.py output  columns: id, body, translated")
    _block("translated (English pivot)", article["english_body"])
    _counts("translated", article["english_body"])

    print("\n[3] summary.py output    columns: id, body, translated, summary")
    print("    summary is ENGLISH at this stage (ml80 / rp5.0 in the real file name).")
    _block("summary (English)", article["english_summary"])
    _counts("english summary", article["english_summary"])

    print("\n[4] translate_back.py    columns: id, body, summary")
    print("    English columns are dropped; summary is now Danish silver label.")
    _block("summary (Danish silver)", article["danish_summary"])
    _counts("danish summary", article["danish_summary"])

    print("\n[5] finetune.py reads the Danish pair as encoder/decoder text")
    print(f"    encoder  body     truncated to 1024 tokens in the real trainer")
    print(f"    decoder  summary  truncated to 128 tokens in the real trainer")
    print(f"    this sample split file: sample_{article['split']}_split.csv")

    ratio = len(word_tokenize(article["danish_summary"])) / max(
        1, len(word_tokenize(article["danish_body"]))
    )
    print(f"\ncompression (words, danish summary / body): {ratio:.3f}")
    print("A real filter might drop pairs with ratio > 0.5 or < 0.02.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", dest="article_id", default="da-001")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        for article in ARTICLES:
            print(f"{article['id']}\t{article['split']}")
        return
    if args.article_id not in articles_by_id():
        raise SystemExit(f"unknown id {args.article_id}")
    walk(args.article_id)


if __name__ == "__main__":
    main()
