#!/usr/bin/env python3
"""Show how the same article packs at the demo budget vs a production-sized one.

At ``--budget 16`` (the chunking demo default) a long Danish sentence is first
split on a *character* cap, so SYN-004 shreds into fragments. That is the 2023
unit mismatch described in docs/02-chunking-and-length.md.

At ``--budget 40`` the same article mostly stays in sentence-sized pieces and
packs a few sentences per window.

At ``--budget 460`` (90 percent of OPUS-MT's 512) the whole sample article fits
in one pack — which is what the real factory would do for these short texts.

Usage (from repo root):

    python examples/compare_budgets.py
    python examples/compare_budgets.py --id SYN-004 --budgets 16,40,460
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
    packs_to_windows,
    trace_article,
)

SAMPLE_CSV = Path(__file__).resolve().parent / "data" / "sample_articles.csv"
DEFAULT_BUDGETS = (16, 40, 460)


def load_article(path: Path, article_id: str) -> str:
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["id"] == article_id:
                return row["article text"]
    raise SystemExit(f"unknown id: {article_id}")


def summarize_trace(trace, tokenizer) -> str:
    sums = trace.pack_token_sums(tokenizer)
    windows = packs_to_windows(trace.packs)
    lines = [
        f"budget={trace.text_max_length:<4d}  pieces={trace.n_source_sentences:<3d}  "
        f"packs={trace.n_packs:<3d}  tok_sums={sums}",
    ]
    for i, window in enumerate(windows, start=1):
        snippet = window.replace("\n", " ")
        if len(snippet) > 88:
            snippet = snippet[:85] + "..."
        lines.append(f"    P{i}: {snippet}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", default="SYN-004", help="Article id (default: SYN-004)")
    parser.add_argument(
        "--budgets",
        default=",".join(str(b) for b in DEFAULT_BUDGETS),
        help="Comma-separated pack budgets (default: 16,40,460)",
    )
    parser.add_argument("--csv", type=Path, default=SAMPLE_CSV)
    args = parser.parse_args(argv)

    budgets = [int(part.strip()) for part in args.budgets.split(",") if part.strip()]
    if not budgets:
        print("no budgets", file=sys.stderr)
        return 2

    ensure_nltk()
    tokenizer = WhitespaceTokenizer()
    article = load_article(args.csv, args.id)
    print(f"compare_budgets  id={args.id}  n_chars={len(article)}")
    print("whitespace tokenizer; special token included in each piece length")
    print()
    for budget in budgets:
        trace = trace_article(args.id, article, budget, tokenizer)
        print(summarize_trace(trace, tokenizer))
        print()
    print(
        "Lesson: a tiny budget + the character-based long-sentence splitter "
        "invents fragments the 512-token factory would never see."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
