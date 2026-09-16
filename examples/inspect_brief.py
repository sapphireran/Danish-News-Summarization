#!/usr/bin/env python3
"""Pretty-print one Kystlinje brief and its entity telescope."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kystlinje.align import render_alignment
from kystlinje.corpus import brief_by_id
from kystlinje.ledger import build_ledger


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("id", nargs="?", default="kz-07")
    args = parser.parse_args()
    brief = brief_by_id(args.id)
    ledger = build_ledger(brief)
    print(brief.title_da)
    print("=" * len(brief.title_da))
    print(brief.body_da)
    print()
    print("alignment into silver:")
    print(render_alignment(brief, hop="silver"))
    print()
    print(
        "survival  "
        f"pivot={ledger.survival_rate('pivot'):.2f}  "
        f"summary={ledger.survival_rate('summary'):.2f}  "
        f"silver={ledger.survival_rate('silver'):.2f}  "
        f"lead2={ledger.survival_rate('lead2'):.2f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
