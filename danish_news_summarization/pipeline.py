"""CPU-only dry run of the 2023 label-generation pipeline.

Nothing here calls a translation or summarization model. Each neural
stage is replaced by a transparent stand-in so you can inspect chunk
boundaries, CSV schemas, and compression ratios on the sample articles
in ``examples/data/``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Sequence

from .chunking import TokenizerLike, WhitespaceTokenizer, split_article
from .sample_data import SampleArticle
from .schema import project_row, validate_table


@dataclass
class DryRunRecord:
    """One article as it moves through the silver-label pipeline."""

    id: str
    body: str
    translated: str
    english_summary: str
    danish_summary: str
    translation_chunks: List[str] = field(default_factory=list)
    summary_chunks: List[str] = field(default_factory=list)

    def as_stage(self, stage: str) -> Dict[str, str]:
        row = {
            "id": self.id,
            "article text": self.body,
            "body": self.body,
            "translated": self.translated,
            "summary": self.english_summary if stage == "summarized" else self.danish_summary,
        }
        return project_row(stage, row)


@dataclass
class DryRunReport:
    records: List[DryRunRecord]
    tokenizer_name: str
    text_max_length: int

    def tables(self) -> Dict[str, List[Dict[str, str]]]:
        stages = ("raw_articles", "translated", "summarized", "labeled")
        tables = {stage: [record.as_stage(stage) for record in self.records] for stage in stages}
        for stage, rows in tables.items():
            validate_table(stage, rows)
        return tables

    def compression_rows(self) -> List[Dict[str, object]]:
        rows: List[Dict[str, object]] = []
        for record in self.records:
            body_words = len(record.body.split())
            summary_words = len(record.danish_summary.split())
            rows.append(
                {
                    "id": record.id,
                    "danish_words": body_words,
                    "english_words": len(record.translated.split()),
                    "english_summary_words": len(record.english_summary.split()),
                    "danish_summary_words": summary_words,
                    "compression": round(summary_words / body_words, 3) if body_words else 0.0,
                    "translation_windows": len(record.translation_chunks),
                    "summary_windows": len(record.summary_chunks),
                }
            )
        return rows


TranslateFn = Callable[[str, str], str]
SummarizeFn = Callable[[str], str]


def identity_translate(text: str, direction: str) -> str:
    """Mark text with a direction tag instead of running OPUS-MT."""
    return f"[{direction}] {text}"


def lead_sentence_summary(text: str, max_sentences: int = 2) -> str:
    """Cheap extractive stand-in: keep the first ``max_sentences`` sentences."""
    from .text import sent_tokenize

    sentences = sent_tokenize(text)
    if not sentences:
        return text.strip()
    return " ".join(sentences[:max_sentences])


def run_dry_pipeline(
    articles: Sequence[SampleArticle],
    *,
    tokenizer: TokenizerLike | None = None,
    text_max_length: int = 80,
    translate_fn: TranslateFn | None = None,
    summarize_fn: SummarizeFn | None = None,
    use_reference_labels: bool = True,
) -> DryRunReport:
    """Run the four label-generation stages on in-memory sample articles.

    When ``use_reference_labels`` is true (the default), English translations
    and both summaries come from the hand-written sample set. Chunking still
    runs, so you can see how many windows a 512-ish budget would have
    produced. Set it to false to exercise the stub translate/summarize
    functions instead.
    """
    tokenizer = tokenizer or WhitespaceTokenizer()
    translate_fn = translate_fn or identity_translate
    summarize_fn = summarize_fn or lead_sentence_summary

    records: List[DryRunRecord] = []
    for article in articles:
        translation_chunks = split_article(article.body, text_max_length, tokenizer)
        if use_reference_labels:
            translated = article.translation
            english_summary = article.english_summary
            danish_summary = article.danish_summary
        else:
            translated_parts = [translate_fn(chunk, "da→en") for chunk in translation_chunks]
            translated = " ".join(translated_parts)
            english_summary = summarize_fn(translated)
            danish_summary = translate_fn(english_summary, "en→da")

        summary_chunks = split_article(translated, text_max_length, tokenizer)
        records.append(
            DryRunRecord(
                id=article.id,
                body=article.body,
                translated=translated,
                english_summary=english_summary,
                danish_summary=danish_summary,
                translation_chunks=translation_chunks,
                summary_chunks=summary_chunks,
            )
        )

    name = type(tokenizer).__name__
    return DryRunReport(records=records, tokenizer_name=name, text_max_length=text_max_length)
