#!/usr/bin/env python3
"""Validate toy (or any) CSVs against the 2023 column contracts.

    python examples/validate_schema.py
    python examples/validate_schema.py --articles path/to/file.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

from dns_examples.io import ids_of, read_csv  # noqa: E402
from dns_examples.paths import DATA_DIR, SPLITS_DIR  # noqa: E402
from dns_examples.schema import (  # noqa: E402
    STAGE_LABELS,
    ValidationIssue,
    align_id_sets,
    validate_rows,
    validate_split_partition,
)


def _fieldnames(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            return next(reader)
        except StopIteration:
            return []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--articles", type=Path, default=None)
    parser.add_argument("--translated", type=Path, default=None)
    parser.add_argument("--summaries-en", type=Path, default=None)
    parser.add_argument("--labeled", type=Path, default=None)
    parser.add_argument("--train", type=Path, default=None)
    parser.add_argument("--validation", type=Path, default=None)
    parser.add_argument("--test", type=Path, default=None)
    parser.add_argument("--allow-extra", action="store_true")
    return parser


def _check_stage(path: Path, stage: str, allow_extra: bool) -> list[ValidationIssue]:
    rows = read_csv(path)
    report = validate_rows(rows, stage, fieldnames=_fieldnames(path), allow_extra=allow_extra)
    return report.issues


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data = args.data_dir
    paths = {
        "articles": args.articles or data / "sample_articles.csv",
        "translated": args.translated or data / "sample_translated.csv",
        "summaries_en": args.summaries_en or data / "sample_summaries_en.csv",
        "labeled": args.labeled or data / "sample_labeled.csv",
    }
    split_paths = {
        "train": args.train or SPLITS_DIR / "train.csv",
        "validation": args.validation or SPLITS_DIR / "validation.csv",
        "test": args.test or SPLITS_DIR / "test.csv",
    }

    issues: list[ValidationIssue] = []
    id_sets: dict[str, list[str]] = {}

    for stage, path in paths.items():
        if not path.exists():
            issues.append(ValidationIssue("missing_file", f"{STAGE_LABELS[stage]}: {path} not found"))
            continue
        stage_issues = _check_stage(path, stage, args.allow_extra)
        issues.extend(stage_issues)
        id_sets[stage] = ids_of(read_csv(path))
        extra = f" ({len(stage_issues)} issue(s))" if stage_issues else " ok"
        print(f"{stage:13} {path}{extra}")

    if "articles" in id_sets and "translated" in id_sets:
        issues.extend(
            align_id_sets(id_sets["articles"], id_sets["translated"], left_name="articles", right_name="translated")
        )
    if "articles" in id_sets and "summaries_en" in id_sets:
        issues.extend(
            align_id_sets(
                id_sets["articles"],
                id_sets["summaries_en"],
                left_name="articles",
                right_name="summaries_en",
            )
        )
    if "articles" in id_sets and "labeled" in id_sets:
        issues.extend(
            align_id_sets(id_sets["articles"], id_sets["labeled"], left_name="articles", right_name="labeled")
        )

    split_ids: dict[str, list[str]] = {}
    for name, path in split_paths.items():
        if not path.exists():
            issues.append(ValidationIssue("missing_file", f"split {name}: {path} not found"))
            continue
        split_issues = _check_stage(path, "labeled", args.allow_extra)
        issues.extend(split_issues)
        split_ids[name] = ids_of(read_csv(path))
        extra = f" ({len(split_issues)} issue(s))" if split_issues else " ok"
        print(f"split/{name:9} {path}{extra}")

    if "labeled" in id_sets and len(split_ids) == 3:
        issues.extend(
            validate_split_partition(
                id_sets["labeled"],
                split_ids.get("train", []),
                split_ids.get("validation", []),
                split_ids.get("test", []),
            )
        )

    if issues:
        print()
        print(f"{len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print()
    print("all schema checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
