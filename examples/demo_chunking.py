#!/usr/bin/env python3
"""Show how a Danish sample article is packed into encoder windows.

    python3 examples/demo_chunking.py
    python3 examples/demo_chunking.py --id dn-001 --text-max-length 180
    python3 examples/demo_chunking.py --all --text-max-length 220
"""

from __future__ import annotations

import argparse
import textwrap

from chunking import (
    char_budget_len,
    default_text_max_length,
    simple_sent_tokenize,
    split_into_windows,
    window_stats,
)
from sample_articles import ARTICLES, by_id, ids


def render_article(article_id: str, text_max_length: int, width: int) -> str:
    article = by_id(article_id)
    text = article["article_text"]
    stats = window_stats(text, text_max_length)
    windows = split_into_windows(text, text_max_length)
    sentences = simple_sent_tokenize(text)

    lines = [
        f"id: {article_id}",
        f"chars: {stats['chars']}",
        f"sentences: {len(sentences)}",
        f"windows @ budget {text_max_length}: {stats['windows']}",
        f"window char-budget lengths: "
        + ", ".join(str(char_budget_len(" ".join(window))) for window in windows),
        "",
        "source:",
        textwrap.fill(text, width=width),
        "",
    ]
    for index, window in enumerate(windows, start=1):
        joined = " ".join(window)
        lines.append(f"window {index} ({char_budget_len(joined)}):")
        lines.append(textwrap.fill(joined, width=width))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", default="dn-001", choices=ids())
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--text-max-length", type=int, default=default_text_max_length())
    parser.add_argument("--width", type=int, default=88)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    chosen = [article["id"] for article in ARTICLES] if args.all else [args.id]
    blocks = [render_article(article_id, args.text_max_length, args.width) for article_id in chosen]
    print("\n".join(blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
