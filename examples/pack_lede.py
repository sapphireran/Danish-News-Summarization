#!/usr/bin/env python3
"""Pack one Danish body with the course-like budgets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sejeroe.cli import main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", default="SEJ-001")
    parser.add_argument(
        "--policy",
        default="",
        help="Optional preset such as manchet-tight or forward-hop",
    )
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    argv = ["pack", "--id", args.id]
    if args.policy:
        argv.extend(["--policy", args.policy])
    raise SystemExit(main(argv))
