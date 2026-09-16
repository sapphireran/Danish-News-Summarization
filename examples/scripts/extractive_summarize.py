#!/usr/bin/env python3
"""Lead-N extractive stand-in for summary.py.

This is not the English T5 teacher. It exists so a dry-run can produce a
summary column without a GPU. Default is the first two sentences of the
chosen column, which is the classic news lead baseline.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from text_lib import lead_n_sentences, read_csv, write_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True)
    parser.add_argument("--column", required=True, help="Text to summarize")
    parser.add_argument("--sentences", type=int, default=2)
    parser.add_argument(
        "--output",
        help="Write a CSV copy with an extra summary column. Default: stdout table",
    )
    parser.add_argument(
        "--summary-column",
        default="summary",
        help="Name of the written summary column",
    )
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    return parser


def summarize_rows(rows: list[dict[str, str]], column: str, sentences: int) -> list[dict[str, str]]:
    out = []
    for row in rows:
        item = dict(row)
        item["_extractive"] = lead_n_sentences(row.get(column, ""), sentences)
        out.append(item)
    return out


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = read_csv(args.path)
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("No rows", file=sys.stderr)
        return 1
    if args.column not in rows[0]:
        print(f"Column {args.column!r} not in {list(rows[0])}", file=sys.stderr)
        return 2

    summarized = summarize_rows(rows, args.column, args.sentences)
    payload = [
        {
            "id": row.get("id", ""),
            "source_column": args.column,
            "sentences": args.sentences,
            "summary": row["_extractive"],
        }
        for row in summarized
    ]

    if args.output:
        written = []
        for row in summarized:
            item = {key: value for key, value in row.items() if key != "_extractive"}
            item[args.summary_column] = row["_extractive"]
            written.append(item)
        fieldnames = list(written[0].keys())
        write_csv(args.output, written, fieldnames)
        print(f"wrote {len(written)} rows to {args.output}", file=sys.stderr)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if not args.output:
        for item in payload:
            print("-" * 72)
            print(f"id={item['id']}")
            print(item["summary"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
