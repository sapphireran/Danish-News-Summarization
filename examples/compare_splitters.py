#!/usr/bin/env python3
"""Compare naive regex splits with the Danish news splitter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pakhus.cli import _cmd_split
from pakhus.corpus import ARTICLE_BY_ID


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", default="tof-003", choices=sorted(ARTICLE_BY_ID))
    args = parser.parse_args()
    return _cmd_split(args)


if __name__ == "__main__":
    raise SystemExit(main())
