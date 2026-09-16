#!/usr/bin/env python3
"""Compare article vs summary lengths on an aligned labeled CSV.

Useful for spotting the chunk-then-concatenate problem: if mean summary
tokens approach the 128-token fine-tune cap, later windows are wasted.
"""

from __future__ import annotations

import argparse
import json
import sys

from text_lib import approximate_token_len, mean, read_csv, split_sentences, word_tokens


def percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    index = (len(ordered) - 1) * q
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def column_stats(rows: list[dict[str, str]], column: str) -> dict[str, float | int]:
    char_lengths = [len(row.get(column, "") or "") for row in rows]
    word_lengths = [len(word_tokens(row.get(column, "") or "")) for row in rows]
    token_lengths = [approximate_token_len(row.get(column, "") or "", add_special_tokens=False) for row in rows]
    sent_lengths = [len(split_sentences(row.get(column, "") or "")) for row in rows]
    return {
        "rows": len(rows),
        "chars_mean": round(mean(float(v) for v in char_lengths), 1),
        "chars_p50": round(percentile(char_lengths, 0.5), 1),
        "chars_p90": round(percentile(char_lengths, 0.9), 1),
        "words_mean": round(mean(float(v) for v in word_lengths), 1),
        "approx_tokens_mean": round(mean(float(v) for v in token_lengths), 1),
        "approx_tokens_max": max(token_lengths) if token_lengths else 0,
        "sentences_mean": round(mean(float(v) for v in sent_lengths), 2),
        "over_128_tokens": sum(1 for value in token_lengths if value > 128),
        "over_1024_tokens": sum(1 for value in token_lengths if value > 1024),
    }


def compression(rows: list[dict[str, str]], source: str, target: str) -> dict[str, float]:
    ratios = []
    for row in rows:
        source_len = len(word_tokens(row.get(source, "") or ""))
        target_len = len(word_tokens(row.get(target, "") or ""))
        if source_len:
            ratios.append(target_len / source_len)
    return {
        "word_compression_mean": round(mean(ratios), 3) if ratios else 0.0,
        "pairs": len(ratios),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True)
    parser.add_argument("--source-col", default="body")
    parser.add_argument("--target-col", default="summary")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = read_csv(args.path)
    if not rows:
        print("No rows", file=sys.stderr)
        return 1
    for column in (args.source_col, args.target_col):
        if column not in rows[0]:
            print(f"Missing column {column!r}", file=sys.stderr)
            return 2

    report = {
        "path": args.path,
        "source": {args.source_col: column_stats(rows, args.source_col)},
        "target": {args.target_col: column_stats(rows, args.target_col)},
        "compression": compression(rows, args.source_col, args.target_col),
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"path: {args.path}")
    print(f"rows: {len(rows)}")
    for title, column, stats in (
        ("source", args.source_col, report["source"][args.source_col]),
        ("target", args.target_col, report["target"][args.target_col]),
    ):
        print(f"\n{title} ({column})")
        print(f"  chars mean/p50/p90: {stats['chars_mean']} / {stats['chars_p50']} / {stats['chars_p90']}")
        print(f"  words mean:         {stats['words_mean']}")
        print(f"  approx tokens mean: {stats['approx_tokens_mean']}  max={stats['approx_tokens_max']}")
        print(f"  sentences mean:     {stats['sentences_mean']}")
        print(f"  over 128 tokens:    {stats['over_128_tokens']}")
        print(f"  over 1024 tokens:   {stats['over_1024_tokens']}")
    comp = report["compression"]
    print(f"\nword compression (target/source): {comp['word_compression_mean']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
