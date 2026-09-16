#!/usr/bin/env python3
"""The 2023 scripts mixed two length notions. This prints both.

``split_long_sentence`` accumulated ``len(word) + 1``.
``split_into_sentences`` asked the OPUS tokenizer for a piece count.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fjordpress.cli import main
from fjordpress.corpus import all_articles

if __name__ == "__main__":
    sentence = all_articles()[0].danish_sentences[1]
    raise SystemExit(main(["counter", "--text", sentence]))
