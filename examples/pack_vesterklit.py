#!/usr/bin/env python3
"""Show 2023-style packing windows on the Vesterklit gazette.

The course scripts used a 460-piece OPUS budget. That swallows each of
these short stories in one window, so the demo uses 40 word-tokens to
make the greedy packer visible.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fjordpress.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["pack", "--budget", "40", "-v"]))
