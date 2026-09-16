#!/usr/bin/env python3
"""Preview what finetune.py would truncate on the synthetic splits.

``finetune.py`` tokenizes ``body`` to 1024 and ``summary`` to 128 with the
mT5 tokenizer. This script uses whitespace tokens as a lower bound: if a
row already exceeds those caps in whole words, a subword tokenizer will
truncate at least as aggressively.

    python examples/demo_finetune_preview.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csv_io import DATA_DIR, read_csv, require_columns  # noqa: E402

BODY_MAX = 1024
SUMMARY_MAX = 128


def token_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def load_split(name: str) -> list[dict]:
    path = DATA_DIR / name
    rows = read_csv(path)
    require_columns(rows, ["id", "body", "summary"], name)
    return rows


def describe(split: str, rows: list[dict]) -> dict:
    bodies = [token_count(row["body"]) for row in rows]
    summaries = [token_count(row["summary"]) for row in rows]
    ratios = [
        summaries[i] / bodies[i] if bodies[i] else 0.0 for i in range(len(rows))
    ]
    would_trunc_body = [row["id"] for row, n in zip(rows, bodies) if n > BODY_MAX]
    would_trunc_sum = [row["id"] for row, n in zip(rows, summaries) if n > SUMMARY_MAX]
    empty = [row["id"] for row in rows if not row["summary"].strip()]
    longer_than_body = [
        row["id"]
        for row, b, s in zip(rows, bodies, summaries)
        if b and s >= b
    ]
    return {
        "split": split,
        "rows": len(rows),
        "body_tokens": {
            "min": min(bodies) if bodies else 0,
            "mean": round(mean(bodies), 1) if bodies else 0,
            "max": max(bodies) if bodies else 0,
        },
        "summary_tokens": {
            "min": min(summaries) if summaries else 0,
            "mean": round(mean(summaries), 1) if summaries else 0,
            "max": max(summaries) if summaries else 0,
        },
        "summary_over_body": {
            "min": round(min(ratios), 3) if ratios else 0,
            "mean": round(mean(ratios), 3) if ratios else 0,
            "max": round(max(ratios), 3) if ratios else 0,
        },
        "ids_truncated_body_at_1024": would_trunc_body,
        "ids_truncated_summary_at_128": would_trunc_sum,
        "ids_empty_summary": empty,
        "ids_summary_not_shorter": longer_than_body,
    }


def main() -> int:
    splits = {
        "train": load_split("sample_train_dataset.csv"),
        "validation": load_split("sample_validation_dataset.csv"),
        "test": load_split("sample_test_dataset.csv"),
    }
    reports = [describe(name, rows) for name, rows in splits.items()]

    all_ids = [row["id"] for rows in splits.values() for row in rows]
    if len(all_ids) != len(set(all_ids)):
        raise SystemExit("duplicate ids across splits")

    print(json.dumps({"body_max": BODY_MAX, "summary_max": SUMMARY_MAX, "splits": reports}, indent=2))
    print(file=sys.stderr)
    print(
        f"{'split':<12} {'n':>3}  {'body max':>8}  {'sum max':>7}  {'ratio mean':>10}  trunc?",
        file=sys.stderr,
    )
    for report in reports:
        flag = (
            "yes"
            if report["ids_truncated_body_at_1024"] or report["ids_truncated_summary_at_128"]
            else "no"
        )
        print(
            f"{report['split']:<12} {report['rows']:>3}  "
            f"{report['body_tokens']['max']:>8}  "
            f"{report['summary_tokens']['max']:>7}  "
            f"{report['summary_over_body']['mean']:>10}  {flag}",
            file=sys.stderr,
        )
    print(
        "\nWhitespace tokens are a lower bound on mT5 subwords. "
        "demo-006 is long as *one sentence* but still well under 1024 words.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
