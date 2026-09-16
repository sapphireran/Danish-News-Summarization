#!/usr/bin/env python3
"""Run every CPU example: rebuild samples, tests, validation, inspection."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable

STEPS = (
    ["examples/data/build_samples.py"],
    ["examples/chunking/test_article_chunker.py"],
    ["examples/validation/test_schema.py"],
    ["examples/configs/check_configs.py"],
    ["examples/validation/validate_samples.py"],
    ["examples/chunking/demo_chunking.py"],
    ["examples/inspection/inspect_dataset.py"],
    ["examples/inspection/print_pipeline_io.py", "--id", "sample-003"],
)


def main() -> int:
    for args in STEPS:
        print(f"\n$ {PY} {' '.join(args)}")
        completed = subprocess.run([PY, *args], cwd=REPO)
        if completed.returncode != 0:
            print(f"FAILED ({completed.returncode}): {args[0]}")
            return completed.returncode
    print("\nall example steps exited 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
