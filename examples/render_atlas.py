#!/usr/bin/env python3
"""Write the HTML window atlas to examples/report/index.html."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pakhus.export import write_lab_data
from pakhus.hops import run_corpus
from pakhus.paths import DATA_DIR, REPORT_DIR
from pakhus.report import write_report


def main() -> int:
    cascade = run_corpus()
    write_lab_data(DATA_DIR, cascade)
    path = write_report(REPORT_DIR, cascade)
    sys.stdout.write(f"wrote {path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
