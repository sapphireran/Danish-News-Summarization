#!/usr/bin/env python3
"""Validate a pipeline CSV against the documented column contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from text_lib import (
    DATA_DIR,
    inspect_rows,
    load_expected_columns,
    looks_like_danish,
    read_csv,
    unicode_letter_ratio,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        required=True,
        help="One of the keys in examples/data/expected_columns.json",
    )
    parser.add_argument("--path", required=True, help="CSV to inspect")
    parser.add_argument(
        "--contracts",
        default=str(DATA_DIR / "expected_columns.json"),
        help="Override the contract file",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    return parser


def language_notes(rows: list[dict[str, str]], spec: dict) -> list[str]:
    notes: list[str] = []
    languages = spec.get("languages") or {}
    if not rows:
        return notes
    sample = rows[0]
    for column, lang in languages.items():
        text = sample.get(column, "")
        if not text:
            continue
        danish = looks_like_danish(text)
        if lang == "da" and not danish:
            notes.append(
                f"Column {column!r} is marked Danish but the first row has no common Danish markers."
            )
        if lang == "en" and danish and unicode_letter_ratio(text) > 0.7:
            # The dry-run stub may leave Danish in an English column on purpose.
            notes.append(
                f"Column {column!r} is marked English but the first row still looks Danish."
            )
    return notes


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    contracts = load_expected_columns(Path(args.contracts))
    stages = contracts.get("stages") or {}
    if args.stage not in stages:
        known = ", ".join(sorted(stages))
        print(f"Unknown stage {args.stage!r}. Known: {known}", file=sys.stderr)
        return 2

    path = Path(args.path)
    if not path.is_file():
        print(f"Missing file: {path}", file=sys.stderr)
        return 2

    spec = stages[args.stage]
    rows = read_csv(path)
    report = inspect_rows(rows, args.stage, path, spec)
    report.notes.extend(language_notes(rows, spec))

    if args.json:
        print(json.dumps(report.as_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"stage:            {report.stage}")
        print(f"path:             {report.path}")
        print(f"rows:             {report.rows}")
        print(f"required:         {', '.join(report.required)}")
        print(f"missing columns:  {', '.join(report.missing_columns) or '—'}")
        print(f"extra columns:    {', '.join(report.extra_columns) or '—'}")
        print(f"duplicate ids:    {', '.join(report.duplicate_ids) or '—'}")
        print("empty cells:")
        for column, count in report.empty_cells.items():
            print(f"  {column}: {count}")
        if report.char_lengths:
            print("char lengths:")
            for column, stats in report.char_lengths.items():
                print(
                    f"  {column}: min={stats['min']:.0f} mean={stats['mean']:.1f} max={stats['max']:.0f}"
                )
        if report.notes:
            print("notes:")
            for note in report.notes:
                print(f"  - {note}")
        print(f"ok:               {report.ok}")

    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
