#!/usr/bin/env python3
"""Print scars still present in the frozen 2023 course scripts."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pakhus.scars import scan_repo


def main() -> int:
    report = scan_repo()
    sys.stdout.write(report.render())
    return 0 if report.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
