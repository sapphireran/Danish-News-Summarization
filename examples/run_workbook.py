#!/usr/bin/env python3
"""Run the download-free Kystlinje workbook end to end (stdlib only)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS = [
    [sys.executable, "-m", "kystlinje", "list"],
    [sys.executable, "-m", "kystlinje", "show", "kz-07"],
    [sys.executable, "-m", "kystlinje", "ledger"],
    [sys.executable, "-m", "kystlinje", "ledger", "--id", "kz-05"],
    [sys.executable, "-m", "kystlinje", "align", "kz-08"],
    [sys.executable, "-m", "kystlinje", "pack", "kz-03", "--budget", "80"],
    [sys.executable, "-m", "kystlinje", "schemas"],
    [sys.executable, "-m", "kystlinje", "quiz", "--answers"],
    [sys.executable, "-m", "kystlinje", "validate"],
    [sys.executable, "-m", "kystlinje", "write-tables"],
    [sys.executable, "-m", "kystlinje", "report"],
]


def main() -> int:
    print(f"workbook root: {ROOT}")
    for command in COMMANDS:
        print("\n$ " + " ".join(command))
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            print(f"command failed with {completed.returncode}", file=sys.stderr)
            return completed.returncode
    print("\nall workbook commands exited 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
