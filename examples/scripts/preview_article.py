#!/usr/bin/env python3
"""Print every committed fixture column for one synthetic article id."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from text_lib import DATA_DIR, read_csv

FIXTURES = (
    ("source", DATA_DIR / "sample_articles.csv"),
    ("translated", DATA_DIR / "sample_translated.csv"),
    ("summarized", DATA_DIR / "sample_summarized.csv"),
    ("labeled", DATA_DIR / "sample_labeled.csv"),
)

PREFERRED_ORDER = (
    "id",
    "article text",
    "body",
    "translated",
    "summary",
    "input_text",
    "target_text",
)


def index_fixture(path: Path) -> dict[str, dict[str, str]]:
    return {row.get("id", ""): row for row in read_csv(path)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", dest="article_id", help="Fixture id, for example demo-001")
    parser.add_argument("--list-ids", action="store_true", help="Print ids and quit")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    loaded = {name: index_fixture(path) for name, path in FIXTURES}
    ids = sorted(loaded["source"])
    if args.list_ids:
        for key in ids:
            print(key)
        return 0
    if not args.article_id:
        print("Pass --id demo-001 or --list-ids", file=sys.stderr)
        return 2
    if args.article_id not in loaded["source"]:
        print(f"Unknown id {args.article_id!r}. Try --list-ids", file=sys.stderr)
        return 2

    bundle = {name: loaded[name].get(args.article_id, {}) for name in loaded}
    if args.json:
        print(json.dumps(bundle, indent=2, ensure_ascii=False))
        return 0

    print(f"id: {args.article_id}")
    for stage, row in bundle.items():
        print("=" * 72)
        print(stage)
        if not row:
            print("  (missing)")
            continue
        keys = [key for key in PREFERRED_ORDER if key in row]
        keys.extend(key for key in row if key not in keys)
        for key in keys:
            if key == "id":
                continue
            print(f"\n[{key}]")
            print(row[key])
    return 0


if __name__ == "__main__":
    sys.exit(main())
