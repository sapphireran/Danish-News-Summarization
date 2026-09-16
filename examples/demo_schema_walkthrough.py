#!/usr/bin/env python3
"""Validate the synthetic CSVs against the 2023 stage schemas.

Checks column names, id stability across stages, UTF-8 Danish letters,
and that the fine-tune split partitions the labeled set without overlap.

    python examples/demo_schema_walkthrough.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csv_io import (  # noqa: E402
    DATA_DIR,
    danish_letters_present,
    read_csv,
    read_jsonl,
    require_columns,
)

SCHEMAS = {
    "sample_source_articles.csv": ["id", "article text"],
    "sample_translated_articles.csv": ["id", "body", "translated"],
    "sample_summarized.csv": ["id", "body", "translated", "summary"],
    "sample_labeled_dataset.csv": ["id", "body", "summary"],
    "sample_train_dataset.csv": ["id", "body", "summary"],
    "sample_validation_dataset.csv": ["id", "body", "summary"],
    "sample_test_dataset.csv": ["id", "body", "summary"],
}


def ids_of(path: Path) -> list[str]:
    return [row["id"] for row in read_csv(path)]


def main() -> int:
    report = {"files": {}, "errors": []}

    for name, columns in SCHEMAS.items():
        path = DATA_DIR / name
        if not path.exists():
            report["errors"].append(f"missing {name}")
            continue
        rows = read_csv(path)
        require_columns(rows, columns, name)
        bodies = []
        for row in rows:
            if name == "sample_source_articles.csv":
                bodies.append(row["article text"])
            else:
                bodies.append(row.get("body", ""))
        has_danish = any(danish_letters_present(text) for text in bodies)
        report["files"][name] = {
            "rows": len(rows),
            "columns": columns,
            "danish_letters_in_body": has_danish,
            "ids": [row["id"] for row in rows],
        }
        if not has_danish:
            report["errors"].append(f"{name}: no æ/ø/å in article bodies (encoding?)")

    source_ids = set(ids_of(DATA_DIR / "sample_source_articles.csv"))
    for name in (
        "sample_translated_articles.csv",
        "sample_summarized.csv",
        "sample_labeled_dataset.csv",
    ):
        other = set(ids_of(DATA_DIR / name))
        if other != source_ids:
            report["errors"].append(f"{name}: ids {sorted(other)} != source {sorted(source_ids)}")

    labeled = read_csv(DATA_DIR / "sample_labeled_dataset.csv")
    labeled_by_id = {row["id"]: row for row in labeled}

    split_names = [
        "sample_train_dataset.csv",
        "sample_validation_dataset.csv",
        "sample_test_dataset.csv",
    ]
    seen: set[str] = set()
    for name in split_names:
        for row in read_csv(DATA_DIR / name):
            if row["id"] in seen:
                report["errors"].append(f"id {row['id']} appears in more than one split")
            seen.add(row["id"])
            gold = labeled_by_id.get(row["id"])
            if gold is None:
                report["errors"].append(f"{name}: {row['id']} not in labeled set")
            elif gold["summary"] != row["summary"]:
                report["errors"].append(f"{name}: {row['id']} summary drifted from labeled set")
    if seen != source_ids:
        report["errors"].append(
            f"splits cover {sorted(seen)} but labeled/source have {sorted(source_ids)}"
        )

    eval_rows = read_jsonl(DATA_DIR / "sample_public_eval.jsonl")
    for row in eval_rows:
        for key in ("input_text", "target_text"):
            if key not in row:
                report["errors"].append(f"public eval row missing {key}")
        if row.get("input_text") and not danish_letters_present(row["input_text"]):
            report["errors"].append(f"{row.get('id')}: eval input has no Danish letters")
    report["public_eval_rows"] = len(eval_rows)

    # Language checks on a couple of columns that must stay English / Danish.
    summarized = read_csv(DATA_DIR / "sample_summarized.csv")
    for row in summarized:
        if danish_letters_present(row["summary"]):
            report["errors"].append(
                f"{row['id']}: English stage summary unexpectedly contains æ/ø/å"
            )
        if not danish_letters_present(row["body"]):
            report["errors"].append(f"{row['id']}: summarized body lost Danish letters")

    labeled = read_csv(DATA_DIR / "sample_labeled_dataset.csv")
    for row in labeled:
        if not danish_letters_present(row["summary"]):
            report["errors"].append(f"{row['id']}: silver summary has no Danish letters")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["errors"]:
        print(f"\n{len(report['errors'])} schema problem(s).", file=sys.stderr)
        return 1
    print(
        f"\nOK: {len(report['files'])} CSVs and {report['public_eval_rows']} "
        "public-eval rows match the 2023 schemas.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
