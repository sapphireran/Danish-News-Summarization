#!/usr/bin/env python3
"""Walk the silver-labeling stages using the checked-in sample CSVs.

This does not call OPUS-MT or T5. It joins the fictional example tables
the same way the root scripts join model outputs, then checks that ids
line up from the raw dump to the labeled file.

Run from the repository root:

    python3 examples/simulate_labeling_pipeline.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_summarization.schema import validate_frame

DATA = Path(__file__).resolve().parent / "data"


def read_rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_frame(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    if not rows:
        return {}
    return {key: [row[key] for row in rows] for key in rows[0]}


def preview(text: str, width: int = 88) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= width else flat[: width - 3] + "..."


def main() -> int:
    raw = read_rows("sample_articles.csv")
    translated = read_rows("sample_translated.csv")
    summarized = read_rows("sample_summarized.csv")
    labeled = read_rows("sample_labeled.csv")

    stages = (
        ("raw", raw),
        ("translated", translated),
        ("summarized", summarized),
        ("labeled", labeled),
    )
    for stage, rows in stages:
        problems = validate_frame(as_frame(rows), stage)
        if problems:
            print(f"{stage}: " + "; ".join(problems))
            return 1

    raw_ids = [row["id"] for row in raw]
    if [row["id"] for row in labeled] != raw_ids:
        print("labeled ids drifted from the raw sample dump")
        return 1

    print("Silver-label walkthrough on fictional sample rows")
    print("Models are not called. Each stage is a checked-in CSV.")
    print()

    by_translated = {row["id"]: row for row in translated}
    by_summarized = {row["id"]: row for row in summarized}
    by_labeled = {row["id"]: row for row in labeled}

    for row in raw:
        article_id = row["id"]
        print(f"== {article_id} ==")
        print("Danish body:")
        print("  " + preview(row["article text"]))
        print("English pivot:")
        print("  " + preview(by_translated[article_id]["translated"]))
        print("English summary (T5 stand-in):")
        print("  " + preview(by_summarized[article_id]["summary"]))
        print("Danish silver label:")
        print("  " + preview(by_labeled[article_id]["summary"]))
        print()

    print(f"{len(raw)} articles kept their ids from raw dump to labeled table.")
    print("Next course-project step would be a train/validation/test split.")
    print("See examples/data/sample_train.csv for a two-row toy split.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
