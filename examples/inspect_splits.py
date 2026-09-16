#!/usr/bin/env python3
"""Show how the 12 fictional articles are cut into trainer splits.

Prints genre, character counts, and which evaluation-style summary each id
carries. Useful when you edit sample_corpus.py and want to see the sheet
before regenerating CSVs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.lib.sample_corpus import (  # noqa: E402
    ARTICLES,
    TEST_IDS,
    TRAIN_IDS,
    VALIDATION_IDS,
    split_name,
)


def _line(article: dict) -> str:
    return (
        f"{article['id']:7}  {split_name(article['id']):10}  "
        f"{article['genre']:10}  "
        f"body={len(article['article_text']):4d}ch  "
        f"pivot={len(article['summary_da_pivot']):3d}ch  "
        f"edit={len(article['summary_da_editorial']):3d}ch"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--split",
        choices=("train", "validation", "test", "all"),
        default="all",
    )
    args = parser.parse_args()

    wanted = {
        "train": set(TRAIN_IDS),
        "validation": set(VALIDATION_IDS),
        "test": set(TEST_IDS),
        "all": {a["id"] for a in ARTICLES},
    }[args.split]

    print("id       split       genre       lengths")
    print("-" * 72)
    shown = 0
    for article in ARTICLES:
        if article["id"] not in wanted:
            continue
        print(_line(article))
        shown += 1
    print("-" * 72)
    print(
        f"{shown} rows  "
        f"train={len(TRAIN_IDS)} val={len(VALIDATION_IDS)} test={len(TEST_IDS)}"
    )


if __name__ == "__main__":
    main()
