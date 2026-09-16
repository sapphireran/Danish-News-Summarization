#!/usr/bin/env python3
"""Write hops, validate them, and refresh the desk notes."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sejeroe.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["all"]))
