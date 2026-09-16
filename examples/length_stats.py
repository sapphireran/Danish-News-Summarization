#!/usr/bin/env python3
"""Print length tables for every committed example stage.

Helps catch a summary that will be truncated at the mT5 128-token target
cap, and shows how many 80- and 460-length packs each Danish body needs.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.lib.text_chunking import default_length_fn, pack_report  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _pad(cell: object, width: int) -> str:
    text = str(cell)
    return text if len(text) >= width else text + " " * (width - len(text))


def _table(headers: list[str], rows: list[list[object]]) -> None:
    widths = [len(h) for h in headers]
    str_rows = [[cell for cell in row] for row in rows]
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    print("  ".join(_pad(h, widths[i]) for i, h in enumerate(headers)))
    print("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in str_rows:
        print("  ".join(_pad(cell, widths[i]) for i, cell in enumerate(row)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA)
    args = parser.parse_args()

    raw = _read(args.data_dir / "raw_danish_articles.csv")
    summarized = {r["id"]: r for r in _read(args.data_dir / "summarized_articles.csv")}
    labeled = {r["id"]: r for r in _read(args.data_dir / "labeled_danish.csv")}

    rows = []
    warn_long_targets = []
    for article in raw:
        body = article["article text"]
        article_id = article["id"]
        packs_80 = pack_report(body, 80, language="danish")
        packs_460 = pack_report(body, 460, language="danish")
        en_sum = summarized[article_id]["summary"]
        da_sum = labeled[article_id]["summary"]
        da_sum_len = default_length_fn(da_sum)
        if da_sum_len > 128:
            warn_long_targets.append(article_id)
        rows.append(
            [
                article_id,
                len(body),
                default_length_fn(body),
                packs_80["n_packs"],
                packs_460["n_packs"],
                default_length_fn(en_sum),
                da_sum_len,
            ]
        )

    print("stage lengths (length columns are the word-fallback tokenizer)")
    print()
    _table(
        [
            "id",
            "body_chars",
            "body_len",
            "packs@80",
            "packs@460",
            "sum_en_len",
            "sum_da_len",
        ],
        rows,
    )
    print()
    print("mT5 target cap in finetune.py is 128.")
    if warn_long_targets:
        print(f"would truncate: {', '.join(warn_long_targets)}")
    else:
        print("no example Danish silver summary exceeds 128 under the fallback counter.")

    eval_rows = _read(args.data_dir / "nordjylland_like_eval.csv")
    print()
    print(f"nordjylland_like_eval.csv rows: {len(eval_rows)}")
    print(
        "  mean text_len="
        f"{sum(int(r['text_len']) for r in eval_rows) / len(eval_rows):.1f}  "
        "mean summary_len="
        f"{sum(int(r['summary_len']) for r in eval_rows) / len(eval_rows):.1f}"
    )


if __name__ == "__main__":
    main()
