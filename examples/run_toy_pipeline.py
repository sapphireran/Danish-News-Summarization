#!/usr/bin/env python3
"""Run the three silver-label hops on the fictional sample articles.

No GPU, no Hugging Face download. Known ids reuse the hand-written
English / Danish strings in `examples/data`. Unknown ids are wrapped in
`[da→en]` / `[en→da]` markers so you can see the hop.

Example:

    python examples/run_toy_pipeline.py
    python examples/run_toy_pipeline.py --budget 20 --output examples/output
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

from dns_examples.io import read_csv  # noqa: E402
from dns_examples.paths import DATA_DIR, OUTPUT_DIR  # noqa: E402
from dns_examples.pipeline import load_default_lexicon, pack_preview, run_toy_pipeline, write_pipeline_csvs  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--articles",
        type=Path,
        default=DATA_DIR / "sample_articles.csv",
        help="Stage-0 CSV with columns id, article text",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Directory holding the hand-written hop fixtures",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for toy_*.csv (gitignored)",
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=40,
        help="Whitespace-token pack budget (2023 Marian budget was 460 subwords)",
    )
    parser.add_argument(
        "--no-split-oversized",
        action="store_true",
        help="Match translate_back.py: do not break long sentences on commas",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    articles = read_csv(args.articles)
    if not articles:
        print(f"no rows in {args.articles}", file=sys.stderr)
        return 2
    lexicon = load_default_lexicon(args.data_dir)
    result = run_toy_pipeline(
        articles,
        lexicon,
        pack_budget=args.budget,
        split_oversized=not args.no_split_oversized,
    )
    written = write_pipeline_csvs(result, args.output)

    print(f"toy pipeline: {len(result.records)} articles, pack budget {result.pack_budget}")
    print()
    for rec in result.records:
        print(f"## {rec.id}")
        print(f"danish sentences packed into {rec.pack_count} group(s)")
        for line in pack_preview(rec):
            print(line)
        print(f"EN summary: {rec.english_summary}")
        print(f"DA silver:  {rec.danish_summary}")
        print()
    print("wrote:")
    for stage, path in written.items():
        print(f"  {stage:12} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
