#!/usr/bin/env python3
"""Validate CSV files against the course-project pipeline schemas."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from examples.schema import PIPELINE_SCHEMAS, format_schema_table, validate_records


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def check_file(path: Path, stage: str) -> list[str]:
    if not path.is_file():
        return [f"{stage}: file not found: {path}"]
    records = read_csv(path)
    return validate_records(records, stage)


def default_example_jobs(repo_root: Path) -> list[tuple[str, Path]]:
    data = repo_root / "examples" / "data"
    return [
        ("raw_articles", data / "sample_articles.csv"),
        ("translated_articles", data / "sample_translated.csv"),
        ("summarized_english", data / "sample_summarized.csv"),
        ("labeled_danish", data / "sample_labeled.csv"),
        ("finetune_split", data / "sample_finetune_train.csv"),
        ("finetune_split", data / "sample_finetune_validation.csv"),
        ("finetune_split", data / "sample_finetune_test.csv"),
    ]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=sorted(PIPELINE_SCHEMAS),
        help="Schema to check. Required together with --file.",
    )
    parser.add_argument("--file", type=Path, help="CSV to validate.")
    parser.add_argument(
        "--list-schemas",
        action="store_true",
        help="Print every stage contract and exit.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_ROOT,
        help="Repository root used to find examples/data.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.list_schemas:
        blocks = [format_schema_table(stage) for stage in PIPELINE_SCHEMAS]
        print("\n\n".join(blocks))
        return 0

    if (args.stage is None) ^ (args.file is None):
        print("error: --stage and --file must be used together", file=sys.stderr)
        return 2

    if args.stage and args.file:
        jobs = [(args.stage, args.file)]
    else:
        jobs = default_example_jobs(args.repo_root)

    failed = 0
    for stage, path in jobs:
        problems = check_file(path, stage)
        if problems:
            failed += 1
            print(f"FAIL  {stage}  {path}")
            for problem in problems:
                print(f"      {problem}")
        else:
            print(f"ok    {stage}  {path}")

    if failed:
        print(f"\n{failed} file(s) failed schema checks", file=sys.stderr)
        return 1
    print(f"\n{len(jobs)} file(s) matched their stage contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
