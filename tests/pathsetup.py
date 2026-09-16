"""Put examples/ on sys.path so tests can import the demo modules."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = REPO_ROOT / "examples"
SAMPLE_DATA = EXAMPLES / "sample_data"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))
