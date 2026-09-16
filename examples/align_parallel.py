#!/usr/bin/env python3
"""Pair Danish and English sentences for one Sejerø brief."""

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
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    raise SystemExit(main(["align", "--id", args.id]))
