#!/usr/bin/env python3
"""Run every offline example and stop on the first failure.

    python examples/run_all.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEMOS = [
    "test_text_chunking.py",
    "demo_schema_walkthrough.py",
    "demo_sentence_chunking.py",
    "demo_pipeline_dry_run.py",
    "demo_finetune_preview.py",
    "demo_offline_metrics.py",
]


def main() -> int:
    python = sys.executable
    for name in DEMOS:
        path = ROOT / name
        print(f"\n=== {name} ===\n", flush=True)
        result = subprocess.run([python, str(path)], cwd=str(ROOT.parent))
        if result.returncode != 0:
            print(f"\nFAILED: {name} (exit {result.returncode})", file=sys.stderr)
            return result.returncode
    print("\nAll offline examples passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
