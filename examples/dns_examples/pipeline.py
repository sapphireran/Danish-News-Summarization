"""Run the three silver-label hops on fixture rows without downloading models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from .chunking import TokenCounter, WhitespaceCounter, groups_to_text, split_into_sentence_groups
from .io import read_csv, write_csv
from .mock_models import (
    HopLexicon,
    summarize_english,
    translate_article,
    translate_summary_back,
)
from .schema import SCHEMAS

EXAMPLES_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = EXAMPLES_ROOT / "data"
DEFAULT_OUTPUT_DIR = EXAMPLES_ROOT / "output"


@dataclass
class HopRecord:
    id: str
    danish: str
    english: str
    english_summary: str
    danish_summary: str
    pack_groups: list[list[str]] = field(default_factory=list)
    pack_budget: int = 0

    @property
    def pack_count(self) -> int:
        return len(self.pack_groups)


@dataclass
class PipelineResult:
    records: list[HopRecord]
    lexicon: HopLexicon
    pack_budget: int

    def articles_rows(self) -> list[dict[str, str]]:
        return [{"id": rec.id, "article text": rec.danish} for rec in self.records]

    def translated_rows(self) -> list[dict[str, str]]:
        return [{"id": rec.id, "body": rec.danish, "translated": rec.english} for rec in self.records]

    def summaries_en_rows(self) -> list[dict[str, str]]:
        return [
            {
                "id": rec.id,
                "body": rec.danish,
                "translated": rec.english,
                "summary": rec.english_summary,
            }
            for rec in self.records
        ]

    def labeled_rows(self) -> list[dict[str, str]]:
        return [{"id": rec.id, "body": rec.danish, "summary": rec.danish_summary} for rec in self.records]


def load_default_lexicon(data_dir: Path | None = None) -> HopLexicon:
    data_dir = data_dir or DATA_DIR
    return HopLexicon.from_fixture_rows(
        articles=read_csv(data_dir / "sample_articles.csv"),
        translated=read_csv(data_dir / "sample_translated.csv"),
        summaries_en=read_csv(data_dir / "sample_summaries_en.csv"),
        labeled=read_csv(data_dir / "sample_labeled.csv"),
    )


def run_toy_pipeline(
    article_rows: Sequence[dict[str, str]],
    lexicon: HopLexicon | None = None,
    *,
    pack_budget: int = 40,
    counter: TokenCounter | None = None,
    split_oversized: bool = True,
) -> PipelineResult:
    """Walk each article through DA→EN, EN summarize, EN→DA.

    `pack_budget` defaults to 40 whitespace-tokens so the long
    Østerhavn sentence actually splits in the demo. The 2023 Marian
    budget was `int(512 * 0.9)` = 460 subword tokens.
    """
    lexicon = lexicon or HopLexicon()
    counter = counter or WhitespaceCounter()
    records: list[HopRecord] = []

    for row in article_rows:
        row_id = row["id"]
        danish = row.get("article text") or row.get("body") or ""
        groups = split_into_sentence_groups(
            danish,
            pack_budget,
            counter,
            split_oversized=split_oversized,
        )
        english = translate_article(row_id, danish, lexicon)
        english_summary = summarize_english(row_id, english, lexicon)
        danish_summary = translate_summary_back(row_id, english_summary, lexicon)
        records.append(
            HopRecord(
                id=row_id,
                danish=danish,
                english=english,
                english_summary=english_summary,
                danish_summary=danish_summary,
                pack_groups=groups,
                pack_budget=pack_budget,
            )
        )
    return PipelineResult(records=records, lexicon=lexicon, pack_budget=pack_budget)


def write_pipeline_csvs(result: PipelineResult, output_dir: Path | None = None) -> dict[str, Path]:
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    mapping = {
        "articles": (result.articles_rows(), SCHEMAS["articles"]),
        "translated": (result.translated_rows(), SCHEMAS["translated"]),
        "summaries_en": (result.summaries_en_rows(), SCHEMAS["summaries_en"]),
        "labeled": (result.labeled_rows(), SCHEMAS["labeled"]),
    }
    written: dict[str, Path] = {}
    filenames = {
        "articles": "toy_articles.csv",
        "translated": "toy_translated.csv",
        "summaries_en": "toy_summaries_en.csv",
        "labeled": "toy_labeled.csv",
    }
    for stage, (rows, fields) in mapping.items():
        path = output_dir / filenames[stage]
        write_csv(path, rows, fields)
        written[stage] = path
    return written


def pack_preview(record: HopRecord) -> list[str]:
    """One line per packed group, for the CLI report."""
    texts = groups_to_text(record.pack_groups)
    return [f"  pack {index}/{record.pack_count}: {text}" for index, text in enumerate(texts, start=1)]
