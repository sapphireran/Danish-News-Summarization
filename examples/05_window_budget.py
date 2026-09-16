"""Show how the window count on one article changes with the length budget.

The course scripts used a 512-token model limit and packed at 90% of that.
This table uses word counts so the effect is visible on the short fixtures
without a Hugging Face tokenizer.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news.chunking import measure, split_into_windows, split_sentences
from danish_news.reporting import pad_columns
from examples.data.corpus import by_id


DEFAULT_BUDGETS = (20, 40, 60, 80, 120, 200, 400)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article-id", default="harbour-plan")
    parser.add_argument(
        "--budgets",
        default=",".join(str(value) for value in DEFAULT_BUDGETS),
        help="Comma-separated word budgets to compare.",
    )
    parser.add_argument(
        "--unit",
        choices=("chars", "words", "tokens"),
        default="words",
    )
    args = parser.parse_args(argv)

    catalog = by_id()
    if args.article_id not in catalog:
        print(f"unknown article id {args.article_id!r}", file=sys.stderr)
        return 2

    article = catalog[args.article_id]
    text = article["article_text"]
    sentences = split_sentences(text)
    budgets = [int(part.strip()) for part in args.budgets.split(",") if part.strip()]

    print(f"article:    {article['id']}")
    print(f"title:      {article['title']}")
    print(f"sentences:  {len(sentences)}")
    print(f"words:      {measure(text, 'words')}")
    print(f"chars:      {measure(text, 'chars')}")
    print()

    rows = []
    for budget in budgets:
        windows = split_into_windows(text, budget, args.unit)
        overflow = [window for window in windows if window.unit_count > budget]
        rows.append(
            {
                "budget": budget,
                "windows": len(windows),
                "mean_fill": (
                    sum(window.unit_count for window in windows) / len(windows)
                    if windows
                    else 0.0
                ),
                "max_fill": max((window.unit_count for window in windows), default=0),
                "over_budget": len(overflow),
                "first_window_sents": len(windows[0].texts) if windows else 0,
            }
        )
    print(pad_columns(rows, ("budget", "windows", "mean_fill", "max_fill", "over_budget", "first_window_sents")))
    print()
    print(
        "A 512-token OPUS-MT window is much larger than these word budgets. "
        "The harbour-plan fixture is long enough that a 40-word cap already "
        "splits it, which is the behaviour translate.py relies on for 10k articles."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
