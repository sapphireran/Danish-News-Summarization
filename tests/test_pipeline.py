from __future__ import annotations

from danish_news.glossary import GlossaryBackend
from danish_news.pipeline import labeled_rows, run_pivot, summarized_rows, translated_rows
from danish_news.schemas import validate_rows
from examples.data.corpus import ARTICLES


def _raw_rows() -> list[dict[str, str]]:
    return [
        {"id": article["id"], "article text": article["article_text"]}
        for article in ARTICLES
    ]


def test_glossary_translates_known_phrase() -> None:
    backend = GlossaryBackend()
    out = backend.translate_da_en(["Kommunalbestyrelsen vedtog planen."])
    assert "city council" in out[0].lower()


def test_run_pivot_emits_all_stages() -> None:
    records = run_pivot(_raw_rows(), GlossaryBackend())
    assert len(records) == len(ARTICLES)
    harbour = next(record for record in records if record.id == "harbour-plan")
    assert harbour.windows
    assert harbour.translated
    assert harbour.summary_en
    assert harbour.summary

    validate_rows(translated_rows(records), "translated")
    validate_rows(summarized_rows(records), "summarized_en")
    validate_rows(labeled_rows(records), "labeled")


def test_summarize_keeps_leading_sentences() -> None:
    backend = GlossaryBackend()
    text = "First sentence is kept. Second sentence is also kept. Third is dropped."
    summary = backend.summarize_en(text)
    assert "First sentence" in summary
    assert "Third is dropped" not in summary
