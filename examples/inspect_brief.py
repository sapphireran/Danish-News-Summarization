#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from maalestok.cli import main as maalestok_main  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Show one Blåhøj brief.")
    parser.add_argument("article_id", nargs="?", default="bh-02")
    args = parser.parse_args()
    return maalestok_main(["show", args.article_id])


if __name__ == "__main__":
    raise SystemExit(main())
