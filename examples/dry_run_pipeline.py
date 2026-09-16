#!/usr/bin/env python3
"""Walk the silver-label pipeline using only the committed example fixtures.

No CTranslate2 conversion, no T5 download, no GPU. The script loads each stage
CSV, checks columns, and prints what the next original root script would consume.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news_sum.config import DA_EN, EN_DA, ENGLISH_NEWS_T5, MT5_LARGE
from danish_news_sum.dataset import (
    RAW_COLUMNS,
    SILVER_COLUMNS,
    SUMMARIZED_COLUMNS,
    TRANSLATED_COLUMNS,
    load_article_csv,
    summarize_dataset,
    validate_columns,
    window_plan,
)

DATA = Path(__file__).resolve().parent / "data"

STAGES = [
    {
        "step": 1,
        "name": "raw Danish articles",
        "csv": DATA / "sample_danish_articles.csv",
        "columns": RAW_COLUMNS,
        "next_script": "translate.py",
        "note": "Original input filename was 10000_articles_without_linebreaks.csv.",
    },
    {
        "step": 2,
        "name": "Danish + English bodies",
        "csv": DATA / "sample_translated_articles.csv",
        "columns": TRANSLATED_COLUMNS,
        "next_script": "summary.py",
        "note": "English column is fed to mrm8488/t5-base-finetuned-summarize-news.",
    },
    {
        "step": 3,
        "name": "English summaries still aligned to Danish bodies",
        "csv": DATA / "sample_english_summaries.csv",
        "columns": SUMMARIZED_COLUMNS,
        "next_script": "translate_back.py",
        "note": "Only the English summary is translated back; the Danish body stays put.",
    },
    {
        "step": 4,
        "name": "silver Danish labels",
        "csv": DATA / "sample_labeled_danish.csv",
        "columns": SILVER_COLUMNS,
        "next_script": "finetune.py",
        "note": "Split this schema into datasets/train_dataset.csv and friends before training.",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max-length", type=int, default=80)
    args = parser.parse_args()

    report = []
    for stage in STAGES:
        rows = load_article_csv(stage["csv"])
        validate_columns(rows, stage["columns"], label=stage["csv"].name)
        body_field = "article text" if "article text" in rows[0] else "body"
        stats = summarize_dataset(rows, body_field=body_field, summary_field="summary")
        plan = window_plan(rows, text_max_length=args.max_length)
        report.append(
            {
                "step": stage["step"],
                "name": stage["name"],
                "csv": stage["csv"].name,
                "rows": len(rows),
                "columns": list(stage["columns"]),
                "next_script": stage["next_script"],
                "note": stage["note"],
                "stats": stats.as_dict(),
                "mean_windows": round(sum(item["window_count"] for item in plan) / len(plan), 2),
            }
        )

    payload = {
        "models": {
            "da_en": DA_EN.source_model,
            "en_da": EN_DA.source_model,
            "english_summarizer": ENGLISH_NEWS_T5.model_name,
            "finetune": MT5_LARGE.model_name,
        },
        "stages": report,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("Silver-label pipeline dry run (example fixtures only)")
    print(f"  DA→EN model     {DA_EN.source_model}")
    print(f"  EN summarizer   {ENGLISH_NEWS_T5.model_name}")
    print(f"  EN→DA model     {EN_DA.source_model}")
    print(f"  fine-tune base  {MT5_LARGE.model_name}")
    print()
    for stage in report:
        print(f"Step {stage['step']}: {stage['name']}")
        print(f"  file          {stage['csv']}")
        print(f"  rows          {stage['rows']}")
        print(f"  columns       {', '.join(stage['columns'])}")
        print(f"  next script   {stage['next_script']}")
        print(f"  mean windows  {stage['mean_windows']} (budget {args.max_length} whitespace tokens)")
        print(f"  {stage['note']}")
        print()
    print("To run the original GPU pipeline, start at Ctranslate_converter.py. See docs/reproduction.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
