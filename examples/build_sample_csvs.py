"""Build the example stage CSVs from `examples/data/corpus.py`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news.schemas import write_csv  # noqa: E402
from examples.data.corpus import ARTICLES  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"


def build(data_dir: Path = DATA_DIR) -> dict[str, Path]:
    raw = [
        {"id": article["id"], "article text": article["article_text"]}
        for article in ARTICLES
    ]
    translated = [
        {
            "id": article["id"],
            "body": article["article_text"],
            "translated": article["translated"],
        }
        for article in ARTICLES
    ]
    summarized = [
        {
            "id": article["id"],
            "body": article["article_text"],
            "translated": article["translated"],
            "summary": article["summary_en"],
        }
        for article in ARTICLES
    ]
    labeled = [
        {
            "id": article["id"],
            "body": article["article_text"],
            "summary": article["summary_da"],
        }
        for article in ARTICLES
    ]
    references = [
        {
            "id": article["id"],
            "body": article["article_text"],
            "summary": article["reference_da"],
        }
        for article in ARTICLES
    ]
    paths = {
        "raw": write_csv(data_dir / "sample_articles.csv", raw, "raw"),
        "translated": write_csv(
            data_dir / "sample_translated.csv", translated, "translated"
        ),
        "summarized_en": write_csv(
            data_dir / "sample_summaries_en.csv", summarized, "summarized_en"
        ),
        "labeled": write_csv(data_dir / "sample_labeled.csv", labeled, "labeled"),
        "references": write_csv(
            data_dir / "sample_references.csv", references, "labeled"
        ),
    }
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Directory for the generated CSV files.",
    )
    args = parser.parse_args(argv)
    paths = build(args.data_dir)
    for stage, path in paths.items():
        print(f"{stage:16s} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
