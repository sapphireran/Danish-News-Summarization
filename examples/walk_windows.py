#!/usr/bin/env python3
"""Print hop-1 / hop-2 pane bars for one Toftevig article."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pakhus.corpus import ARTICLE_BY_ID
from pakhus.hops import atlas_for


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", default="tof-001", choices=sorted(ARTICLE_BY_ID))
    args = parser.parse_args()
    sys.stdout.write(atlas_for(args.article))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
