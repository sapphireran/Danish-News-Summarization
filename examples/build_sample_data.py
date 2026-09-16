#!/usr/bin/env python3
"""Write examples/sample_data/*.csv from sample_articles.py.

    python3 examples/build_sample_data.py
    python3 examples/build_sample_data.py --output-dir examples/sample_data
"""

from __future__ import annotations

import argparse
from pathlib import Path

from csv_util import write_rows
from sample_articles import ARTICLES
from schema import REQUIRED_COLUMNS, SAMPLE_FILENAMES
from split_labeled_dataset import write_splits

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "examples" / "sample_data"


def build(output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    articles = [
        {"id": item["id"], "article text": item["article_text"]} for item in ARTICLES
    ]
    translated = [
        {"id": item["id"], "body": item["article_text"], "translated": item["translated"]}
        for item in ARTICLES
    ]
    summarized = [
        {
            "id": item["id"],
            "body": item["article_text"],
            "translated": item["translated"],
            "summary": item["summary_en"],
        }
        for item in ARTICLES
    ]
    labeled = [
        {"id": item["id"], "body": item["article_text"], "summary": item["summary_da"]}
        for item in ARTICLES
    ]

    written = {
        "articles": output_dir / SAMPLE_FILENAMES["articles"],
        "translated": output_dir / SAMPLE_FILENAMES["translated"],
        "summarized": output_dir / SAMPLE_FILENAMES["summarized"],
        "labeled": output_dir / SAMPLE_FILENAMES["labeled"],
    }
    write_rows(written["articles"], REQUIRED_COLUMNS["articles"], articles)
    write_rows(written["translated"], REQUIRED_COLUMNS["translated"], translated)
    write_rows(written["summarized"], REQUIRED_COLUMNS["summarized"], summarized)
    write_rows(written["labeled"], REQUIRED_COLUMNS["labeled"], labeled)

    split_paths = write_splits(
        input_path=written["labeled"],
        output_dir=output_dir,
        train_ratio=8 / 12,
        val_ratio=2 / 12,
        seed=2023,
        sample_names=True,
    )
    for name, path in split_paths.items():
        written[f"split_{name}"] = path
    return written


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    written = build(args.output_dir)
    for name, path in written.items():
        print(f"{name:18} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
