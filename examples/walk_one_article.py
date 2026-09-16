#!/usr/bin/env python3
"""Print every pipeline view of a single sample article.

Useful when you are writing docs or debugging a schema mismatch: you can
see the Danish body, the English translation, the English summary, and
the Danish silver label side by side.

    PYTHONPATH=. python examples/walk_one_article.py dn-002
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news_summarization.chunking import WhitespaceTokenizer, split_article
from danish_news_summarization.sample_data import get_article
from danish_news_summarization.schema import describe_stage


def _block(title: str, body: str) -> None:
    print(title)
    print("-" * len(title))
    print(body)
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("article_id", nargs="?", default="dn-001")
    parser.add_argument("--max-length", type=int, default=50)
    args = parser.parse_args()

    article = get_article(args.article_id)
    tokenizer = WhitespaceTokenizer()
    windows = split_article(article.body, args.max_length, tokenizer)

    print(f"{article.id} — {article.title}")
    print(f"{article.city} / {article.topic}")
    print()
    _block("Stage raw_articles  (column: article text)", article.body)
    _block("Stage translated  (column: translated)", article.translation)
    _block("Stage summarized  (column: summary, still English)", article.english_summary)
    _block("Stage labeled / finetune  (column: summary, Danish)", article.danish_summary)

    print(f"Packed into {len(windows)} windows at budget {args.max_length}:")
    for index, window in enumerate(windows, start=1):
        print(f"  [{index}] {window[:120]}{'...' if len(window) > 120 else ''}")
    print()
    print(describe_stage("labeled"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
