#!/usr/bin/env python3
"""Walk the four silver-label stages on the fictional sample set.

By default the English translations and both summaries come from the
hand-written fixtures (so the CSVs look like a finished run). Pass
``--stubs`` to replace those with the identity-translate + lead-sentence
stand-ins — useful when you want to see how error markers propagate.

    PYTHONPATH=. python examples/dry_run_pipeline.py
    PYTHONPATH=. python examples/dry_run_pipeline.py --stubs --out examples/output/stubs
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news_summarization.cli import main as cli_main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "examples" / "output")
    parser.add_argument("--max-length", type=int, default=80)
    parser.add_argument("--stubs", action="store_true")
    args = parser.parse_args()

    argv = ["dry-run", "--out", str(args.out), "--max-length", str(args.max_length)]
    if args.stubs:
        argv.append("--stubs")
    code = cli_main(argv)
    stats = Path(args.out) / "compression_stats.json"
    if stats.exists():
        rows = json.loads(stats.read_text(encoding="utf-8"))
        avg = sum(row["compression"] for row in rows) / len(rows)
        print(f"\nMean summary/body word ratio: {avg:.3f}")
        print("Silver-label pipelines that compress harder than ~0.15 often drop specifics;")
        print("softer than ~0.40 start to look like paraphrases, not summaries.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
