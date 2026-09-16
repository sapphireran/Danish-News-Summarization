#!/usr/bin/env python3
"""Regenerate examples/data CSVs from the Toftevig fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pakhus.export import write_lab_data
from pakhus.paths import DATA_DIR


def main() -> int:
    written = write_lab_data(DATA_DIR)
    for key, path in written.items():
        sys.stdout.write(f"{key:18s}  {path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
