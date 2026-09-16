"""Validate that every example CSV matches the stage schema from the 2023 scripts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news.config import load_config
from danish_news.reporting import pad_columns
from danish_news.schemas import STAGE_SCHEMAS, SchemaError, read_csv


CHECKS = (
    ("raw_csv", "raw"),
    ("translated_csv", "translated"),
    ("summarized_csv", "summarized_en"),
    ("labeled_csv", "labeled"),
    ("references_csv", "labeled"),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    args = parser.parse_args(argv)
    config = load_config(args.config)

    rows = []
    failed = 0
    for field_name, stage in CHECKS:
        path = config.resolve(field_name)
        schema = STAGE_SCHEMAS[stage]
        try:
            records = read_csv(path, stage)
            status = "ok"
            detail = f"{len(records)} rows"
        except (OSError, SchemaError) as exc:
            records = []
            status = "FAIL"
            detail = str(exc)
            failed += 1
        rows.append(
            {
                "file": path.name,
                "stage": stage,
                "required": ", ".join(schema.required),
                "status": status,
                "detail": detail,
            }
        )

    print(pad_columns(rows, ("file", "stage", "required", "status", "detail")))
    print()
    if failed:
        print(f"{failed} file(s) failed schema checks", file=sys.stderr)
        return 1
    print("all example CSVs match the course-script column contracts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
