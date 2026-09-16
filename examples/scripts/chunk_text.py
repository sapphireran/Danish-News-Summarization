#!/usr/bin/env python3
"""Show the 2023 sentence-packing algorithm on a CSV column.

Token lengths here are regex approximations, not OPUS-MT lengths. Use a
small --max-tokens value on the synthetic articles to force multiple
windows the way a 512-token model would on a long news feature.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from text_lib import pack_sentences, read_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True, help="CSV file")
    parser.add_argument("--column", required=True, help="Text column to pack")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=460,
        help="Window budget. 460 matches 512 * 0.9 in translate.py",
    )
    parser.add_argument(
        "--no-split-overlong",
        action="store_true",
        help="Skip the comma/word overflow splitter (like translate_back.py)",
    )
    parser.add_argument("--limit", type=int, default=0, help="Only pack the first N rows")
    parser.add_argument("--id-column", default="id")
    parser.add_argument("--json", action="store_true")
    return parser


def pack_row(row: dict[str, str], column: str, max_tokens: int, split_overlong: bool) -> dict:
    text = row.get(column, "") or ""
    windows = pack_sentences(text, max_tokens, split_overlong=split_overlong)
    return {
        "id": row.get("id", ""),
        "column": column,
        "chars": len(text),
        "windows": [
            {
                "index": index,
                "sentences": window.sentences,
                "token_lengths": window.token_lengths,
                "token_count": window.token_count,
                "text": window.as_text(),
            }
            for index, window in enumerate(windows)
        ],
        "window_count": len(windows),
        "approx_tokens": sum(window.token_count for window in windows),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.path)
    rows = read_csv(path)
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print(f"No rows in {path}", file=sys.stderr)
        return 1
    if args.column not in rows[0]:
        print(f"Column {args.column!r} not in {list(rows[0])}", file=sys.stderr)
        return 2

    reports = [
        pack_row(row, args.column, args.max_tokens, not args.no_split_overlong) for row in rows
    ]

    if args.json:
        print(json.dumps(reports, indent=2, ensure_ascii=False))
        return 0

    for report in reports:
        print("=" * 72)
        print(f"id={report['id']}  chars={report['chars']}  windows={report['window_count']}  "
              f"approx_tokens={report['approx_tokens']}")
        for window in report["windows"]:
            preview = window["text"]
            if len(preview) > 160:
                preview = preview[:157] + "..."
            print(
                f"  [{window['index']}] tokens={window['token_count']} "
                f"sents={len(window['sentences'])}  {preview}"
            )
    print("=" * 72)
    print(f"rows={len(reports)}  max_tokens={args.max_tokens}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
