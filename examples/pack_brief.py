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
    parser = argparse.ArgumentParser(description="Pack one brief like 2023.")
    parser.add_argument("article_id", nargs="?", default="bh-05")
    parser.add_argument("--budget", type=int, default=40)
    args = parser.parse_args()
    return maalestok_main(["pack", args.article_id, "--budget", str(args.budget)])


if __name__ == "__main__":
    raise SystemExit(main())
