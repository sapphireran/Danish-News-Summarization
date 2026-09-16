#!/usr/bin/env python3
"""Pretty-print a couple of example articles next to their silver fields.

Useful when reading the docs: you can see the Danish body, the stand-in
English pivot, both summaries, and the toy prediction without opening
five CSVs.
"""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

from corpus import ARTICLES, by_id  # noqa: E402

WRAP = 88


def wrap(title: str, body: str) -> str:
    paragraph = textwrap.fill(body, width=WRAP)
    return f"{title}\n{paragraph}"


def render(article_id: str) -> str:
    article = by_id()[article_id]
    blocks = [
        f"=== {article.id}  split={article.split} ===",
        wrap("Danish body", article.body_da),
        wrap("English body (pivot stand-in)", article.body_en),
        wrap("English silver summary", article.summary_en),
        wrap("Danish silver summary", article.summary_da),
        wrap("Toy prediction (on purpose imperfect)", article.toy_prediction_da),
    ]
    if article.notes:
        blocks.append(f"Note: {article.notes}")
    return "\n\n".join(blocks)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "ids",
        nargs="*",
        default=["dn-001", "dn-006"],
        help="Article ids to print (default: dn-001 and the long dn-006)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print all ids and splits, then exit",
    )
    args = parser.parse_args()
    if args.list:
        for article in ARTICLES:
            print(f"{article.id}\t{article.split}\t{article.notes}")
        return
    unknown = [item for item in args.ids if item not in by_id()]
    if unknown:
        raise SystemExit(f"unknown ids: {unknown}")
    print("\n\n".join(render(article_id) for article_id in args.ids))


if __name__ == "__main__":
    main()
