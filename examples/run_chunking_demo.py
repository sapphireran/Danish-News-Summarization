#!/usr/bin/env python3
"""Print packing traces for the synthetic Danish articles.

Uses a tiny token budget so a short sample article still splits into more than
one window. That is the opposite of production (budget 460–512) and is on
purpose: the demo exists to show the algorithm, not to mimic OPUS-MT.

Usage (from repo root):

    python examples/run_chunking_demo.py
    python examples/run_chunking_demo.py --budget 12 --id SYN-003
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.text_chunking import (  # noqa: E402
    WhitespaceTokenizer,
    ensure_nltk,
    trace_article,
)

SAMPLE_CSV = Path(__file__).resolve().parent / "data" / "sample_articles.csv"
DEFAULT_BUDGET = 16


def load_articles(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def render_trace(trace, tokenizer) -> str:
    lines = [
        f"=== {trace.article_id} ===",
        f"budget (approx tokens): {trace.text_max_length}",
        f"source pieces: {trace.n_source_sentences}",
        f"packs: {trace.n_packs}",
        "",
        "pieces (text[:72], tokens):",
    ]
    for i, (text, length) in enumerate(trace.pairs, start=1):
        snippet = text.replace("\n", " ")
        if len(snippet) > 72:
            snippet = snippet[:69] + "..."
        lines.append(f"  {i:02d}  tok={length:3d}  {snippet}")
    lines.append("")
    lines.append("packs:")
    sums = trace.pack_token_sums(tokenizer)
    for i, (pack, tok_sum) in enumerate(zip(trace.packs, sums), start=1):
        overflow = "  OVER BUDGET" if tok_sum > trace.text_max_length else ""
        preview = " | ".join(s[:40] for s in pack)
        lines.append(
            f"  P{i}  pieces={len(pack)}  tok_sum={tok_sum:3d}{overflow}"
        )
        lines.append(f"      {preview}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--budget",
        type=int,
        default=DEFAULT_BUDGET,
        help="Pack budget in whitespace-approx tokens (default: %(default)s)",
    )
    parser.add_argument(
        "--id",
        action="append",
        dest="ids",
        help="Only trace this SYN- id (repeatable)",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=SAMPLE_CSV,
        help="Articles CSV (default: examples/data/sample_articles.csv)",
    )
    args = parser.parse_args(argv)

    ensure_nltk()
    tokenizer = WhitespaceTokenizer()
    rows = load_articles(args.csv)
    if args.ids:
        wanted = set(args.ids)
        rows = [row for row in rows if row["id"] in wanted]
        missing = wanted - {row["id"] for row in rows}
        if missing:
            print(f"unknown id(s): {sorted(missing)}", file=sys.stderr)
            return 2

    print(
        "Danish-News-Summarization chunking demo\n"
        "Tokenizer: whitespace words + 1 special token\n"
        f"Articles: {args.csv}\n"
    )
    for row in rows:
        article = row["article text"]
        trace = trace_article(row["id"], article, args.budget, tokenizer)
        print(render_trace(trace, tokenizer))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
