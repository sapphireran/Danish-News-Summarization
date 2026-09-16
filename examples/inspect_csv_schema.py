#!/usr/bin/env python3
"""Check the example CSVs against the course-project column contracts.

Run from the repository root:

    python3 examples/inspect_csv_schema.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_summarization.schema import FILE_HINTS, required_columns, validate_frame

DATA = Path(__file__).resolve().parent / "data"

EXAMPLES = (
    ("sample_articles.csv", "raw"),
    ("sample_translated.csv", "translated"),
    ("sample_summarized.csv", "summarized"),
    ("sample_labeled.csv", "labeled"),
    ("sample_train.csv", "train"),
)


def read_table(path: Path) -> dict[str, list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = reader.fieldnames or []
    table = {name: [row[name] for row in rows] for name in columns}
    table["_row_count"] = [str(len(rows))]
    return table


def main() -> int:
    print("Course-project file hints")
    for stage, hint in FILE_HINTS.items():
        print(f"  {stage:12} {hint}")
    print()

    failures = 0
    for filename, stage in EXAMPLES:
        path = DATA / filename
        table = read_table(path)
        row_count = int(table.pop("_row_count")[0])
        problems = validate_frame(table, stage)
        expected = ", ".join(required_columns(stage))
        status = "ok" if not problems else "PROBLEMS"
        print(f"{filename}  ({stage}, {row_count} rows)")
        print(f"  expected: {expected}")
        if problems:
            failures += 1
            for problem in problems:
                print(f"  - {problem}")
        else:
            print(f"  {status}: columns and ids look consistent")
        print()

    if failures:
        print(f"{failures} example table(s) failed the contract")
        return 1
    print("All example tables match the course-project contracts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
