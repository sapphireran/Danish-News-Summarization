#!/usr/bin/env python3
"""Validate pipeline CSVs against the course column contracts.

Checks, per file:

- required columns exist
- ids are unique and non-empty
- required text cells are non-empty
- optional: ids and Danish `body` / `article text` stay aligned across stages

Examples:

    python3 examples/validate_csvs.py --sample-dir examples/sample_data
    python3 examples/validate_csvs.py --path translated_articles.csv --stage translated
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from csv_util import read_rows
from schema import (
    NONEMPTY_COLUMNS,
    SAMPLE_FILENAMES,
    SPLIT_FILENAMES,
    STAGE_0_ARTICLES,
    STAGE_1_TRANSLATED,
    STAGE_2_SUMMARIZED,
    STAGE_3_LABELED,
    STAGE_4_SPLIT,
    SchemaIssue,
    infer_stage_from_filename,
    missing_columns,
    required_columns,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SAMPLE_DIR = REPO_ROOT / "examples" / "sample_data"

BODY_COLUMNS = {
    STAGE_0_ARTICLES: "article text",
    STAGE_1_TRANSLATED: "body",
    STAGE_2_SUMMARIZED: "body",
    STAGE_3_LABELED: "body",
    STAGE_4_SPLIT: "body",
}


def validate_file(path: Path, stage: str) -> list[SchemaIssue]:
    issues: list[SchemaIssue] = []
    try:
        header, rows = read_rows(path)
    except (OSError, ValueError) as exc:
        return [SchemaIssue(str(path), "io", str(exc))]

    missing = missing_columns(stage, header)
    if missing:
        issues.append(
            SchemaIssue(str(path), "columns", f"missing required columns: {missing}")
        )
        return issues

    ids = [row.get("id", "").strip() for row in rows]
    if any(not article_id for article_id in ids):
        issues.append(SchemaIssue(str(path), "empty_id", "one or more rows have an empty id"))

    counts = Counter(article_id for article_id in ids if article_id)
    duplicates = sorted(article_id for article_id, count in counts.items() if count > 1)
    if duplicates:
        issues.append(SchemaIssue(str(path), "duplicate_id", f"duplicate ids: {duplicates}"))

    for column in NONEMPTY_COLUMNS[stage]:
        empties = [
            index
            for index, row in enumerate(rows, start=2)
            if not (row.get(column) or "").strip()
        ]
        if empties:
            preview = empties[:8]
            suffix = "" if len(empties) <= 8 else f" (+{len(empties) - 8} more)"
            issues.append(
                SchemaIssue(
                    str(path),
                    "empty_cell",
                    f"column {column!r} is empty on data rows {preview}{suffix}",
                )
            )

    if not rows:
        issues.append(SchemaIssue(str(path), "empty_file", "no data rows"))

    return issues


def _index_by_id(path: Path, text_column: str) -> dict[str, str]:
    _header, rows = read_rows(path)
    return {row["id"].strip(): row.get(text_column, "") for row in rows if row.get("id", "").strip()}


def validate_alignment(files: dict[str, Path]) -> list[SchemaIssue]:
    """Ids must match across stages, and Danish source text must not drift."""
    issues: list[SchemaIssue] = []
    indexed: dict[str, dict[str, str]] = {}
    for stage, path in files.items():
        try:
            indexed[stage] = _index_by_id(path, BODY_COLUMNS[stage])
        except (OSError, ValueError, KeyError) as exc:
            issues.append(SchemaIssue(str(path), "io", str(exc)))
            return issues

    if STAGE_0_ARTICLES in indexed:
        baseline_stage = STAGE_0_ARTICLES
    elif STAGE_1_TRANSLATED in indexed:
        baseline_stage = STAGE_1_TRANSLATED
    else:
        baseline_stage = next(iter(indexed))

    baseline_ids = set(indexed[baseline_stage])
    for stage, mapping in indexed.items():
        extra = sorted(set(mapping) - baseline_ids)
        missing = sorted(baseline_ids - set(mapping))
        if extra:
            issues.append(
                SchemaIssue(
                    str(files[stage]),
                    "id_set",
                    f"ids not in {baseline_stage}: {extra}",
                )
            )
        if missing:
            issues.append(
                SchemaIssue(
                    str(files[stage]),
                    "id_set",
                    f"missing ids from {baseline_stage}: {missing}",
                )
            )

    if STAGE_0_ARTICLES in indexed:
        source = indexed[STAGE_0_ARTICLES]
        for stage, mapping in indexed.items():
            if stage == STAGE_0_ARTICLES:
                continue
            drifted = sorted(
                article_id
                for article_id, text in mapping.items()
                if article_id in source and text != source[article_id]
            )
            if drifted:
                issues.append(
                    SchemaIssue(
                        str(files[stage]),
                        "body_drift",
                        f"Danish source text differs from stage 0 for ids: {drifted}",
                    )
                )
    return issues


def validate_splits(split_files: dict[str, Path]) -> list[SchemaIssue]:
    issues: list[SchemaIssue] = []
    ids_by_split: dict[str, set[str]] = {}
    for name, path in split_files.items():
        issues.extend(validate_file(path, STAGE_4_SPLIT))
        try:
            ids_by_split[name] = set(_index_by_id(path, "body"))
        except (OSError, ValueError, KeyError) as exc:
            issues.append(SchemaIssue(str(path), "io", str(exc)))
            return issues

    names = list(ids_by_split)
    for left in range(len(names)):
        for right in range(left + 1, len(names)):
            overlap = sorted(ids_by_split[names[left]] & ids_by_split[names[right]])
            if overlap:
                issues.append(
                    SchemaIssue(
                        str(split_files[names[left]]),
                        "split_leak",
                        f"ids also in {names[right]}: {overlap}",
                    )
                )
    return issues


def collect_sample_dir(sample_dir: Path) -> tuple[dict[str, Path], dict[str, Path]]:
    staged: dict[str, Path] = {}
    for stage, filename in SAMPLE_FILENAMES.items():
        path = sample_dir / filename
        if path.exists():
            staged[stage] = path
    splits: dict[str, Path] = {}
    for name, filename in SPLIT_FILENAMES.items():
        path = sample_dir / filename
        if path.exists():
            splits[name] = path
    return staged, splits


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, help="single CSV to check")
    parser.add_argument(
        "--stage",
        choices=sorted(
            {
                STAGE_0_ARTICLES,
                STAGE_1_TRANSLATED,
                STAGE_2_SUMMARIZED,
                STAGE_3_LABELED,
                STAGE_4_SPLIT,
            }
        ),
        help="column contract; inferred from --path when omitted",
    )
    parser.add_argument(
        "--sample-dir",
        type=Path,
        help="directory of sample CSVs (default: examples/sample_data when no --path)",
    )
    parser.add_argument(
        "--skip-alignment",
        action="store_true",
        help="do not compare ids/bodies across stages in --sample-dir",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    issues: list[SchemaIssue] = []

    if args.path is not None:
        stage = args.stage or infer_stage_from_filename(args.path.name)
        if stage is None:
            print(f"cannot infer stage from {args.path.name}; pass --stage", file=sys.stderr)
            return 2
        issues.extend(validate_file(args.path, stage))
    else:
        sample_dir = args.sample_dir or DEFAULT_SAMPLE_DIR
        staged, splits = collect_sample_dir(sample_dir)
        if not staged and not splits:
            print(f"no sample CSVs found in {sample_dir}", file=sys.stderr)
            return 2
        for stage, path in staged.items():
            issues.extend(validate_file(path, stage))
        if not args.skip_alignment and len(staged) > 1:
            issues.extend(validate_alignment(staged))
        if splits:
            issues.extend(validate_splits(splits))

    if issues:
        for issue in issues:
            print(issue)
        print(f"{len(issues)} issue(s)", file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
