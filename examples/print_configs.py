#!/usr/bin/env python3
"""Dump the documented 2023 hyperparameters next to the example JSON files."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news_sum.config import DA_EN, DEFAULT_EVAL, EN_DA, ENGLISH_NEWS_T5, MT5_LARGE, MT5_SMALL

CONFIGS = {
    "translation_da_en": DA_EN,
    "translation_en_da": EN_DA,
    "english_summarizer": ENGLISH_NEWS_T5,
    "finetune_mt5_large": MT5_LARGE,
    "finetune_mt5_small": MT5_SMALL,
    "evaluation": DEFAULT_EVAL,
}


def main() -> int:
    payload = {name: asdict(config) for name, config in CONFIGS.items()}
    payload["translation_da_en"]["text_max_length"] = DA_EN.text_max_length
    payload["translation_en_da"]["text_max_length"] = EN_DA.text_max_length
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
