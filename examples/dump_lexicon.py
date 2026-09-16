#!/usr/bin/env python3
"""Coverage report plus a peek at the closed-world word list."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fjordpress.cli import main
from fjordpress.lexicon import DA_EN

if __name__ == "__main__":
    code = main(["lexicon"])
    sample = sorted(DA_EN.items())[:12]
    print()
    print("first 12 DA→EN entries (alphabetical):")
    for da, en in sample:
        print(f"  {da:20} {en}")
    raise SystemExit(code)
