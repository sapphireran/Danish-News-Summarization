"""Materialise the gazette as the 2023 CSV shapes."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .corpus import GazetteArticle, TRAIN_IDS, TEST_IDS, VALIDATION_IDS, all_articles, articles_for
from .csvio import write_csv
from .hops import HopRecord, run_hops
from .paths import data_dir
from .schemas import (
    LABELED_COLUMNS,
    PUBLIC_EVAL_COLUMNS,
    RAW_INPUT_COLUMNS,
    SPLIT_COLUMNS,
    SUMMARISED_COLUMNS,
    TRANSLATED_COLUMNS,
)
from .tokenize import count_words


def hops_for(article: GazetteArticle, pack_budget: int = 40) -> HopRecord:
    return run_hops(
        article_id=article.article_id,
        danish_sentences=article.danish_sentences,
        english_sentences=article.english_sentences,
        gold_da_summary=article.gold_da_summary,
        gold_en_summary=article.gold_en_summary,
        pack_budget=pack_budget,
    )


def hops_for_all(pack_budget: int = 40) -> List[HopRecord]:
    return [hops_for(art, pack_budget=pack_budget) for art in all_articles()]


def raw_rows(articles: List[GazetteArticle] | None = None) -> List[dict]:
    rows = []
    for art in articles or list(all_articles()):
        rows.append({"id": art.article_id, "article text": art.danish})
    return rows


def translated_rows(records: List[HopRecord]) -> List[dict]:
    rows = []
    for rec in records:
        rows.append(
            {
                "id": rec.article_id,
                "body": rec.danish_source,
                "translated": rec.english_oracle,
            }
        )
    return rows


def summarised_rows(records: List[HopRecord]) -> List[dict]:
    rows = []
    for rec in records:
        rows.append(
            {
                "id": rec.article_id,
                "body": rec.danish_source,
                "translated": rec.english_oracle,
                "summary": rec.english_summary_oracle,
            }
        )
    return rows


def labeled_rows(records: List[HopRecord], use_gold: bool = True) -> List[dict]:
    rows = []
    for rec in records:
        rows.append(
            {
                "id": rec.article_id,
                "body": rec.danish_source,
                "summary": rec.gold_da_summary if use_gold else rec.danish_back_oracle,
            }
        )
    return rows


def public_eval_rows(articles: List[GazetteArticle] | None = None) -> List[dict]:
    rows = []
    for art in articles or list(all_articles()):
        rows.append(
            {
                "input_text": art.danish,
                "target_text": art.gold_da_summary,
                "text_len": count_words(art.danish),
                "summary_len": count_words(art.gold_da_summary),
            }
        )
    return rows


def write_fixtures(target: Path | None = None, pack_budget: int = 40) -> Dict[str, Path]:
    """Write the sample CSVs that the example scripts read."""
    root = target or data_dir()
    root.mkdir(parents=True, exist_ok=True)
    articles = list(all_articles())
    records = hops_for_all(pack_budget=pack_budget)
    index = {rec.article_id: rec for rec in records}

    written: Dict[str, Path] = {}
    written["raw"] = write_csv(root / "00_raw_articles.csv", raw_rows(articles), RAW_INPUT_COLUMNS)
    written["translated"] = write_csv(
        root / "01_translated_articles.csv", translated_rows(records), TRANSLATED_COLUMNS
    )
    written["summarised"] = write_csv(
        root / "02_summarised_articles.csv", summarised_rows(records), SUMMARISED_COLUMNS
    )
    written["labeled"] = write_csv(
        root / "03_labeled_dataset.csv", labeled_rows(records, use_gold=True), LABELED_COLUMNS
    )
    written["labeled_oracle"] = write_csv(
        root / "03_labeled_oracle_back.csv",
        labeled_rows(records, use_gold=False),
        LABELED_COLUMNS,
    )

    for name, ids in (
        ("train", TRAIN_IDS),
        ("validation", VALIDATION_IDS),
        ("test", TEST_IDS),
    ):
        subset = [index[i] for i in ids]
        written[name] = write_csv(
            root / f"04_{name}_dataset.csv",
            labeled_rows(subset, use_gold=True),
            SPLIT_COLUMNS,
        )

    written["public_eval"] = write_csv(
        root / "05_public_eval_shape.csv", public_eval_rows(articles), PUBLIC_EVAL_COLUMNS
    )
    return written
