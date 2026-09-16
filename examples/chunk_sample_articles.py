#!/usr/bin/env python3
"""Show how the 2023 pipeline would pack each sample article into encoder windows.

The original ``translate.py`` / ``summary.py`` scripts use a Hugging Face
tokenizer and a 512-token budget. This walkthrough uses whitespace tokens and a
smaller budget so the committed fixtures actually split on a laptop.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news_sum.dataset import load_article_csv, window_plan

DEFAULT_CSV = Path(__file__).resolve().parent / "data" / "sample_danish_articles.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument(
        "--max-length",
        type=int,
        default=80,
        help="Window budget in whitespace tokens (original scripts use 460–512 model tokens).",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable window plans.")
    args = parser.parse_args()

    rows = load_article_csv(args.csv)
    plan = window_plan(rows, text_max_length=args.max_length)

    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    print(f"Packed {len(plan)} articles from {args.csv.name} with max_length={args.max_length}")
    print()
    for item in plan:
        print(f"[{item['id']}] {item['body_tokens']} tokens -> {item['window_count']} window(s)")
        for window in item["windows"]:
            preview = window["preview"]
            if len(preview) == 160:
                preview = preview.rstrip() + "…"
            print(
                f"    window {window['window_index']:>2}: "
                f"{window['token_count']:>3} tok / {window['char_count']:>4} ch / "
                f"{window['sentence_count']} sent | {preview}"
            )
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
