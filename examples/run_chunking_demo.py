"""Show how a long Danish article is packed into model-sized windows.

Mirrors ``split_article`` in translate.py / summary.py, using the
stand-in word tokenizer so the demo needs no Hub download.

    python examples/run_chunking_demo.py
    python examples/run_chunking_demo.py --max-length 40 --id da-008
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.data.corpus import ARTICLES, articles_by_id
from examples.text_chunking import SimpleWordTokenizer, pack_corpus


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-length", type=int, default=80)
    parser.add_argument("--id", dest="article_id", default=None)
    args = parser.parse_args()

    tokenizer = SimpleWordTokenizer()
    chosen = ARTICLES
    if args.article_id:
        by_id = articles_by_id()
        if args.article_id not in by_id:
            raise SystemExit(f"unknown id {args.article_id}; have {sorted(by_id)}")
        chosen = [by_id[args.article_id]]

    packed = pack_corpus(
        [(article["id"], article["danish_body"]) for article in chosen],
        text_max_length=args.max_length,
        tokenizer=tokenizer,
    )

    print(f"tokenizer=SimpleWordTokenizer  window={args.max_length} ids (incl. BOS/EOS)")
    print("This window is smaller than OPUS/T5's 512 so the 10-article")
    print("sample actually splits. The control flow is the same.\n")

    multi_window = 0
    for item in packed:
        flag = "SPLIT" if len(item.windows) > 1 else "single"
        if len(item.windows) > 1:
            multi_window += 1
        print(
            f"{item.article_id}  {flag}  "
            f"raw_tokens={item.original_tokens}  "
            f"windows={len(item.windows)}  "
            f"per_window={item.token_lengths}"
        )
        if args.article_id or len(item.windows) > 1:
            for index, window in enumerate(item.windows, start=1):
                preview = window if len(window) <= 220 else window[:217] + "..."
                print(f"    [{index}/{len(item.windows)}] {preview}")

    print(
        f"\n{multi_window}/{len(packed)} articles needed more than one window "
        f"at max_length={args.max_length}."
    )
    if args.max_length >= 512:
        print("At 512 (the real OPUS/T5 cap) only the longest samples split.")


if __name__ == "__main__":
    main()
