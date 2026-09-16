#!/usr/bin/env python3
"""Write the committed example CSVs from examples.lib.sample_corpus.

Run from the repository root:

    python examples/data/generate_sample_csvs.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.lib.sample_corpus import (  # noqa: E402
    ARTICLES,
    TEST_IDS,
    TRAIN_IDS,
    VALIDATION_IDS,
    by_id,
)

DATA = Path(__file__).resolve().parent
FINETUNE = DATA / "finetune"


def _write(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def word_count(text: str) -> int:
    return len(text.split())


def main() -> None:
    _write(
        DATA / "raw_danish_articles.csv",
        ["id", "article text"],
        [{"id": a["id"], "article text": a["article_text"]} for a in ARTICLES],
    )
    _write(
        DATA / "translated_articles.csv",
        ["id", "body", "translated"],
        [
            {"id": a["id"], "body": a["article_text"], "translated": a["translated"]}
            for a in ARTICLES
        ],
    )
    _write(
        DATA / "summarized_articles.csv",
        ["id", "body", "translated", "summary"],
        [
            {
                "id": a["id"],
                "body": a["article_text"],
                "translated": a["translated"],
                "summary": a["summary_en"],
            }
            for a in ARTICLES
        ],
    )
    _write(
        DATA / "labeled_danish.csv",
        ["id", "body", "summary"],
        [
            {
                "id": a["id"],
                "body": a["article_text"],
                "summary": a["summary_da_pivot"],
            }
            for a in ARTICLES
        ],
    )

    lookup = by_id()
    for name, ids in (
        ("train_dataset.csv", TRAIN_IDS),
        ("validation_dataset.csv", VALIDATION_IDS),
        ("test_dataset.csv", TEST_IDS),
    ):
        _write(
            FINETUNE / name,
            ["id", "body", "summary"],
            [
                {
                    "id": article_id,
                    "body": lookup[article_id]["article_text"],
                    "summary": lookup[article_id]["summary_da_pivot"],
                }
                for article_id in ids
            ],
        )

    eval_rows = []
    for article in ARTICLES:
        # Keep a smaller eval slice so the file looks like a "mini" split.
        if article["id"] not in {"da-001", "da-004", "da-006", "da-009", "da-012", "da-007"}:
            continue
        eval_rows.append(
            {
                "input_text": article["article_text"],
                "target_text": article["summary_da_editorial"],
                "text_len": word_count(article["article_text"]),
                "summary_len": word_count(article["summary_da_editorial"]),
            }
        )
    _write(
        DATA / "nordjylland_like_eval.csv",
        ["input_text", "target_text", "text_len", "summary_len"],
        eval_rows,
    )
    print(f"Wrote example CSVs under {DATA}")


if __name__ == "__main__":
    main()
