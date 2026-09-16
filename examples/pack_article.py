#!/usr/bin/env python3
"""Run one named packer (course_translate / course_summary / course_back / consistent)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pakhus.cli import _cmd_pack
from pakhus.packing import PACKERS
from pakhus.corpus import ARTICLE_BY_ID


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", required=True, choices=sorted(ARTICLE_BY_ID))
    parser.add_argument("--packer", required=True, choices=sorted(PACKERS))
    args = parser.parse_args()
    return _cmd_pack(args)


if __name__ == "__main__":
    raise SystemExit(main())
