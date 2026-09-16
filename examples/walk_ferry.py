#!/usr/bin/env python3
"""Walk SEJ-001 through the same hops as the 2023 course scripts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sejeroe.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["walk", "--id", "SEJ-001"]))
