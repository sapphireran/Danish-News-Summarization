"""Stage-by-stage helpers that the example dry-run uses.

The GPU course scripts stay in the repository root. This module is the
CPU-only counterpart: it knows the four data stages, how to pack windows,
and how to apply a caller-supplied backend to each window. Backends in the
examples folder are deterministic stand-ins, not OPUS-MT or T5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol

from danish_news.chunking import Unit, Window, split_into_windows
from danish_news.schemas import validate_rows

Translator = Callable[[list[str]], list[str]]
Summarizer = Callable[[str], str]


class Backend(Protocol):
    def translate_da_en(self, sentences: list[str]) -> list[str]: ...

    def summarize_en(self, text: str) -> str: ...

    def translate_en_da(self, sentences: list[str]) -> list[str]: ...


@dataclass(frozen=True)
class PipelineConfig:
    """Window budgets that correspond to the course-script constants."""

    max_units: int = 80
    unit: Unit = "words"
    # `translate.py` used 90% of the 512-token model limit. Examples default
    # to a much smaller word budget so windowing is visible on short fixtures.
    summary_max_sentences: int = 2


@dataclass
class ArticleRecord:
    id: str
    body: str
    translated: str = ""
    summary_en: str = ""
    summary: str = ""
    windows: list[Window] = field(default_factory=list)


def translate_article(
    article: str,
    translate: Translator,
    config: PipelineConfig | None = None,
) -> tuple[str, list[Window]]:
    """Pack `article` into windows and translate each sentence list."""
    cfg = config or PipelineConfig()
    windows = split_into_windows(article, cfg.max_units, cfg.unit)
    pieces: list[str] = []
    for window in windows:
        pieces.extend(translate(list(window.texts)))
    return " ".join(pieces).strip(), windows


def summarize_article(
    english: str,
    summarize: Summarizer,
    config: PipelineConfig | None = None,
) -> str:
    """Summarize each packed window and concatenate the window summaries."""
    cfg = config or PipelineConfig()
    windows = split_into_windows(english, cfg.max_units, cfg.unit)
    return " ".join(summarize(window.text) for window in windows).strip()


def run_pivot(
    rows: list[dict[str, str]],
    backend: Backend,
    config: PipelineConfig | None = None,
) -> list[ArticleRecord]:
    """Run DA→EN → English summary → EN→DA on already-validated raw rows."""
    cfg = config or PipelineConfig()
    validated = validate_rows(rows, "raw")
    records: list[ArticleRecord] = []
    for row in validated:
        record = ArticleRecord(id=row["id"], body=row["article text"])
        record.translated, record.windows = translate_article(
            record.body, backend.translate_da_en, cfg
        )
        record.summary_en = summarize_article(
            record.translated, backend.summarize_en, cfg
        )
        record.summary, _ = translate_article(
            record.summary_en, backend.translate_en_da, cfg
        )
        records.append(record)
    return records


def labeled_rows(records: list[ArticleRecord]) -> list[dict[str, str]]:
    return [{"id": rec.id, "body": rec.body, "summary": rec.summary} for rec in records]


def translated_rows(records: list[ArticleRecord]) -> list[dict[str, str]]:
    return [
        {"id": rec.id, "body": rec.body, "translated": rec.translated} for rec in records
    ]


def summarized_rows(records: list[ArticleRecord]) -> list[dict[str, str]]:
    return [
        {
            "id": rec.id,
            "body": rec.body,
            "translated": rec.translated,
            "summary": rec.summary_en,
        }
        for rec in records
    ]
