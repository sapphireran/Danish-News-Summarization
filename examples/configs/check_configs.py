#!/usr/bin/env python3
"""Sanity-check that the YAML mirrors exist and mention the script defaults.

Avoids a PyYAML dependency: we only look for required substrings.
"""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent

REQUIRED = {
    "convert_models.yaml": (
        "Helsinki-NLP/opus-mt-da-en",
        "Helsinki-NLP/opus-mt-en-da",
        "models/opus-mt-en-da_ct2",
    ),
    "translate.yaml": (
        "10000_articles_without_linebreaks.csv",
        "translated_articles.csv",
        "text_max_length: 460",
    ),
    "summarize.yaml": (
        "mrm8488/t5-base-finetuned-summarize-news",
        "max_length: 80",
        "repetition_penalty: 5.0",
        "debug_row_slice: 10",
    ),
    "translate_back.yaml": (
        "labeled_dataset_ml80_rp5.0.csv",
        "models/opus-mt-en-da_ct2",
    ),
    "finetune_mt5_large.yaml": (
        "google/mt5-large",
        "learning_rate: 0.0003",
        "./large_model",
        "rouge_1_mid_fmeasure",
    ),
    "finetune_mt5_small.yaml": (
        "google/mt5-small",
        "small_model",
    ),
    "eval.yaml": (
        "alexandrainst/nordjylland-news-summarization",
        "xlm-roberta-large",
        "no_repeat_ngram_size: 1",
    ),
}


def main() -> int:
    failed = False
    for name, needles in REQUIRED.items():
        path = HERE / name
        if not path.is_file():
            print(f"[FAIL] missing {path}")
            failed = True
            continue
        text = path.read_text(encoding="utf-8")
        missing = [needle for needle in needles if needle not in text]
        if missing:
            failed = True
            print(f"[FAIL] {name} missing {missing}")
        else:
            print(f"[OK] {name} ({path.stat().st_size} bytes)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
