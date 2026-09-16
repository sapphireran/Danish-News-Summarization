"""Named hops that mirror the 2023 pipeline without calling a model.

The course scripts are:

1. ``Ctranslate_converter.py`` — OPUS weights to CTranslate2.
2. ``translate.py`` — Danish body → English body.
3. ``summary.py`` — English body → English summary (T5 news, max 80).
4. ``translate_back.py`` — English summary → Danish silver label.
5. ``finetune.py`` / ``eval.py`` / ``use_model.py`` — mT5 on the silver CSV.

Here each hop is a hand-written field on ``Article``. Running the hop graph
just projects those fields into the same CSV shapes the root scripts used.
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.models import Article

HOP_ORDER = (
    "raw_da",
    "translated_en",
    "summarized_en",
    "labeled_da",
    "oracle_da",
)


@dataclass(frozen=True)
class HopRecord:
    article_id: str
    hop: str
    text: str
    source_field: str
    course_script: str
    note: str


def hop_records(article: Article) -> tuple[HopRecord, ...]:
    return (
        HopRecord(
            article_id=article.id,
            hop="raw_da",
            text=article.body_da,
            source_field="body_da",
            course_script="(input to translate.py)",
            note="Danish source body. Course input column was 'article text'.",
        ),
        HopRecord(
            article_id=article.id,
            hop="translated_en",
            text=article.body_en,
            source_field="body_en",
            course_script="translate.py",
            note="Hand gloss standing in for opus-mt-da-en + CTranslate2.",
        ),
        HopRecord(
            article_id=article.id,
            hop="summarized_en",
            text=article.summary_en,
            source_field="summary_en",
            course_script="summary.py",
            note="Short T5-news-shaped lede. Course used max_length=80, rp=5.0.",
        ),
        HopRecord(
            article_id=article.id,
            hop="labeled_da",
            text=article.summary_da,
            source_field="summary_da",
            course_script="translate_back.py",
            note="Silver Danish label. Course wrote labeled_dataset_ml80_rp5.0.csv.",
        ),
        HopRecord(
            article_id=article.id,
            hop="oracle_da",
            text=article.oracle_da,
            source_field="oracle_da",
            course_script="(human oracle, not in 2023 scripts)",
            note="Careful Danish manchet written against the gold slot card.",
        ),
    )


def hop_text(article: Article, hop: str) -> str:
    for record in hop_records(article):
        if record.hop == hop:
            return record.text
    raise KeyError(f"unknown hop {hop!r} for {article.id}")
