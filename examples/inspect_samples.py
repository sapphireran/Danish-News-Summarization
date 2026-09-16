#!/usr/bin/env python3
"""Print length and compression stats for the fictional fixtures.

    python examples/inspect_samples.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

from dns_examples.io import read_csv  # noqa: E402
from dns_examples.metrics import summarize_pair, word_tokens  # noqa: E402
from dns_examples.paths import DATA_DIR  # noqa: E402
from dns_examples.sentences import split_sentences  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    articles = {row["id"]: row["article text"] for row in read_csv(args.data_dir / "sample_articles.csv")}
    labeled = {row["id"]: row for row in read_csv(args.data_dir / "sample_labeled.csv")}
    english = {row["id"]: row["translated"] for row in read_csv(args.data_dir / "sample_translated.csv")}
    en_sum = {row["id"]: row["summary"] for row in read_csv(args.data_dir / "sample_summaries_en.csv")}

    print(f"{'id':24} {'da_s':>5} {'da_w':>5} {'en_w':>5} {'en_sum':>6} {'da_sum':>6} {'comp':>6}")
    print("-" * 72)
    for row_id, danish in articles.items():
        scores = summarize_pair(row_id, danish, labeled[row_id]["summary"])
        print(
            f"{row_id:24} {len(split_sentences(danish)):5d} {scores.article_tokens:5d} "
            f"{len(word_tokens(english[row_id])):5d} {len(word_tokens(en_sum[row_id])):6d} "
            f"{scores.summary_tokens:6d} {scores.compression:6.2f}"
        )
    print()
    print("comp = Danish silver tokens / Danish article tokens")
    print("These rows are hand-written fixtures, not model output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
