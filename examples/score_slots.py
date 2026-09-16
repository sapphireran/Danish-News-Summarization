#!/usr/bin/env python3
"""Score slots, quotes, and planted overlap-blind errors."""

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
    parser.add_argument("--id", default="")
    parser.add_argument(
        "--planted",
        action="store_true",
        help="Print JSON lines for the planted errors only",
    )
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    if args.planted:
        raise SystemExit(main(["planted"]))
    argv = ["score"]
    if args.id:
        argv.extend(["--id", args.id])
    raise SystemExit(main(argv))
