#!/usr/bin/env python3
"""Show how the 2023 packer splits the synthetic articles.

Uses the whitespace tokenizer stand-in, then compares the original
character-budget long-sentence splitter with the token-accurate one
on ``demo-006`` (one very long Danish sentence).

    python examples/demo_sentence_chunking.py
    python examples/demo_sentence_chunking.py --max-tokens 40
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow ``python examples/demo_....py`` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from csv_io import DATA_DIR, read_csv, require_columns  # noqa: E402
from text_chunking import (  # noqa: E402
    pack_article,
    simple_sent_tokenize,
    split_long_sentence_char_budget,
    split_long_sentence_token_budget,
    whitespace_tokenizer_len,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=DATA_DIR / "sample_source_articles.csv",
        help="CSV with id,article text",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=40,
        help="Pack budget in whitespace tokens (default 40 so the tiny "
        "fixtures actually split; the course scripts used ~460 subwords)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a JSON report instead of a table",
    )
    return parser.parse_args()


def report_row(article_id: str, text: str, max_tokens: int) -> dict:
    sentences = simple_sent_tokenize(text)
    packed = pack_article(text, max_tokens, split_overlong=True, token_accurate_split=False)
    packed_acc = pack_article(text, max_tokens, split_overlong=True, token_accurate_split=True)
    return {
        "id": article_id,
        "chars": len(text),
        "approx_tokens": whitespace_tokenizer_len(text),
        "sentences": len(sentences),
        "packs_char_splitter": packed.pack_count,
        "packs_token_splitter": packed_acc.pack_count,
        "pack_token_lengths": list(packed.token_lengths),
        "first_pack_preview": packed.as_texts()[0][:160] + ("…" if len(packed.as_texts()[0]) > 160 else ""),
    }


def assert_invariants(rows: list[dict], max_tokens: int) -> None:
    if not rows:
        raise SystemExit("no articles to pack")
    for row in rows:
        if row["sentences"] < 1:
            raise SystemExit(f"{row['id']}: sentence splitter returned nothing")
        if row["packs_char_splitter"] < 1:
            raise SystemExit(f"{row['id']}: packer returned no packs")
        for length in row["pack_token_lengths"]:
            # A single leftover word can theoretically equal the budget.
            if length > max_tokens + 5:
                raise SystemExit(
                    f"{row['id']}: pack length {length} far above budget {max_tokens}"
                )
    long = next((row for row in rows if row["id"] == "demo-006"), None)
    if long and long["sentences"] != 1:
        raise SystemExit("demo-006 should stay one sentence for the splitter demo")
    if long and long["packs_char_splitter"] < 2:
        raise SystemExit(
            "demo-006 should split into multiple packs at the default budget; "
            "lower --max-tokens if you changed the fixtures"
        )


def main() -> int:
    args = parse_args()
    articles = read_csv(args.source)
    require_columns(articles, ["id", "article text"], args.source.name)

    reports = [
        report_row(row["id"], row["article text"], args.max_tokens) for row in articles
    ]
    assert_invariants(reports, args.max_tokens)

    long_text = next(row["article text"] for row in articles if row["id"] == "demo-006")
    char_chunks = split_long_sentence_char_budget(long_text, args.max_tokens)
    token_chunks = split_long_sentence_token_budget(
        long_text, args.max_tokens, whitespace_tokenizer_len
    )

    if args.json:
        print(
            json.dumps(
                {
                    "max_tokens": args.max_tokens,
                    "articles": reports,
                    "demo_006_char_chunks": len(char_chunks),
                    "demo_006_token_chunks": len(token_chunks),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(f"Pack budget: {args.max_tokens} whitespace tokens")
    print(f"{'id':<10} {'tok':>5} {'sent':>5} {'packs':>6} {'acc':>5}  preview")
    print("-" * 88)
    for row in reports:
        print(
            f"{row['id']:<10} {row['approx_tokens']:>5} {row['sentences']:>5} "
            f"{row['packs_char_splitter']:>6} {row['packs_token_splitter']:>5}  "
            f"{row['first_pack_preview']}"
        )

    print()
    print("demo-006 long-sentence splitter")
    print(f"  character-budget chunks (2023 behaviour): {len(char_chunks)}")
    print(f"  token-budget chunks:                      {len(token_chunks)}")
    print("  first character-budget chunk:")
    print(f"    {char_chunks[0][:200]}…")
    print()
    print("Note: course scripts measured this budget in *subword* tokens (~460).")
    print("This demo uses a smaller whitespace budget so six short fixtures split.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
