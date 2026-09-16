#!/usr/bin/env python3
"""Print the hop ledger for one article, then corpus-level means."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fjordpress.cli import main

if __name__ == "__main__":
    article = sys.argv[1] if len(sys.argv) > 1 else "vk-001"
    raise SystemExit(main(["ledger", "--article", article]))
