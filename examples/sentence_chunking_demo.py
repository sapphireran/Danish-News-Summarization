#!/usr/bin/env python3
"""Print sentence packs the way translate.py / summary.py would cut an article.

Uses the longest fictional article by default and two budgets:

* 80  — small enough that you can see several packs on a laptop
* 460 — the 90% × 512 cap the course translation scripts actually use

Pass ``--legacy-long-split`` to use the original char-count cutter.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.lib.text_chunking import pack_report, split_into_sentence_packs  # noqa: E402

DATA = Path(__file__).resolve().parent / "data" / "raw_danish_articles.csv"


def _load_articles(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _pick(rows: list[dict[str, str]], article_id: str | None) -> dict[str, str]:
    if article_id:
        for row in rows:
            if row["id"] == article_id:
                return row
        known = ", ".join(r["id"] for r in rows)
        raise SystemExit(f"unknown id {article_id!r}; have {known}")
    return max(rows, key=lambda row: len(row["article text"]))


def _print_report(title: str, article: str, max_length: int, language: str, legacy: bool) -> None:
    report = pack_report(article, max_length, language=language)
    packs = split_into_sentence_packs(
        article,
        max_length,
        language=language,
        legacy_long_split=legacy,
    )
    print(f"== {title} (max_length={max_length}) ==")
    print(
        f"article_length≈{report['article_length']}  "
        f"sentences={report['n_sentences']}  packs={len(packs)}"
    )
    for i, pack in enumerate(packs, start=1):
        joined = " ".join(pack)
        preview = joined if len(joined) <= 220 else joined[:217] + "..."
        print(f"  pack {i:02d}  n={len(pack):2d}  words≈{len(joined.split()):3d}  {preview}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DATA)
    parser.add_argument("--id", dest="article_id", default=None)
    parser.add_argument(
        "--max-length",
        type=int,
        action="append",
        dest="max_lengths",
        help="repeat to print several budgets (default: 80 and 460)",
    )
    parser.add_argument("--language", default="danish")
    parser.add_argument("--legacy-long-split", action="store_true")
    args = parser.parse_args()

    rows = _load_articles(args.csv)
    if not rows:
        raise SystemExit(f"no rows in {args.csv}")
    row = _pick(rows, args.article_id)
    budgets = args.max_lengths or [80, 460]
    print(f"article {row['id']}  chars={len(row['article text'])}")
    print()
    for budget in budgets:
        _print_report(
            f"{row['id']}",
            row["article text"],
            budget,
            language=args.language,
            legacy=args.legacy_long_split,
        )


if __name__ == "__main__":
    main()
