#!/usr/bin/env python3
"""Show how long Danish articles are packed into model-sized windows.

The GPU scripts call a Hugging Face tokenizer. This example uses the
whitespace stand-in so you can see the *shape* of the algorithm without
downloading OPUS-MT.

    PYTHONPATH=. python examples/chunk_articles.py
    PYTHONPATH=. python examples/chunk_articles.py --max-length 30 --id dn-009
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news_summarization.chunking import WhitespaceTokenizer, split_article
from danish_news_summarization.sample_data import SAMPLE_ARTICLES, get_article


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-length", type=int, default=40)
    parser.add_argument("--id", dest="article_id", default=None)
    args = parser.parse_args()

    articles = (get_article(args.article_id),) if args.article_id else SAMPLE_ARTICLES
    tokenizer = WhitespaceTokenizer()

    print(f"Tokenizer: {type(tokenizer).__name__}  budget: {args.max_length} (incl. 2 specials)\n")
    for article in articles:
        chunks = split_article(article.body, args.max_length, tokenizer)
        print("=" * 78)
        print(f"{article.id}  {article.title}  ({article.city}, {article.topic})")
        print(f"source words: {len(article.body.split())}   windows: {len(chunks)}")
        for index, chunk in enumerate(chunks, start=1):
            token_len = len(tokenizer.encode(chunk))
            print(f"\n--- window {index}/{len(chunks)}  tokens≈{token_len} ---")
            print(chunk)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
