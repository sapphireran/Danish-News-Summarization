"""Write the fictional sample CSVs from corpus.py.

Run from the repository root:

    python examples/data/write_tables.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.data.corpus import ARTICLES, split_rows

HERE = Path(__file__).resolve().parent


def _write(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


def main() -> None:
    _write(
        HERE / "sample_danish_articles.csv",
        ["id", "article text"],
        [
            {"id": article["id"], "article text": article["danish_body"]}
            for article in ARTICLES
        ],
    )
    _write(
        HERE / "sample_translated_articles.csv",
        ["id", "body", "translated"],
        [
            {
                "id": article["id"],
                "body": article["danish_body"],
                "translated": article["english_body"],
            }
            for article in ARTICLES
        ],
    )
    _write(
        HERE / "sample_english_summaries.csv",
        ["id", "body", "translated", "summary"],
        [
            {
                "id": article["id"],
                "body": article["danish_body"],
                "translated": article["english_body"],
                "summary": article["english_summary"],
            }
            for article in ARTICLES
        ],
    )
    _write(
        HERE / "sample_labeled_dataset.csv",
        ["id", "body", "summary"],
        [
            {
                "id": article["id"],
                "body": article["danish_body"],
                "summary": article["danish_summary"],
            }
            for article in ARTICLES
        ],
    )
    _write(
        HERE / "sample_predictions.csv",
        ["id", "reference", "prediction"],
        [
            {
                "id": article["id"],
                "reference": article["danish_summary"],
                "prediction": article["prediction"],
            }
            for article in ARTICLES
        ],
    )
    for split, filename in (
        ("train", "sample_train_split.csv"),
        ("validation", "sample_validation_split.csv"),
        ("test", "sample_test_split.csv"),
    ):
        _write(
            HERE / filename,
            ["id", "body", "summary"],
            [
                {
                    "id": article["id"],
                    "body": article["danish_body"],
                    "summary": article["danish_summary"],
                }
                for article in split_rows(split)
            ],
        )


if __name__ == "__main__":
    main()
