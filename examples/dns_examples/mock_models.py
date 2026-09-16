"""Lookups and cheap stand-ins for the three 2023 model hops.

The real hops are OPUS-MT da-en, a news T5, and OPUS-MT en-da. Those
checkpoints are not in git and should not be downloaded just to show
column shapes. This module:

- serves the hand-written English / Danish strings from `examples/data`
  when an `id` is known;
- falls back to a marked mock (`[da→en] …`) so a new row is still visible
  in the toy output instead of crashing.

Nothing here is a quality claim about Marian or T5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .sentences import split_sentences


@dataclass
class HopLexicon:
    """Per-id strings for each hop, plus optional sentence-aligned pairs."""

    danish: dict[str, str] = field(default_factory=dict)
    english: dict[str, str] = field(default_factory=dict)
    english_summary: dict[str, str] = field(default_factory=dict)
    danish_summary: dict[str, str] = field(default_factory=dict)

    def has(self, row_id: str) -> bool:
        return row_id in self.danish

    @classmethod
    def from_fixture_rows(
        cls,
        *,
        articles: list[Mapping[str, str]] | None = None,
        translated: list[Mapping[str, str]] | None = None,
        summaries_en: list[Mapping[str, str]] | None = None,
        labeled: list[Mapping[str, str]] | None = None,
    ) -> "HopLexicon":
        lex = cls()
        if articles:
            for row in articles:
                lex.danish[row["id"]] = row["article text"]
        if translated:
            for row in translated:
                lex.danish.setdefault(row["id"], row["body"])
                lex.english[row["id"]] = row["translated"]
        if summaries_en:
            for row in summaries_en:
                lex.danish.setdefault(row["id"], row["body"])
                lex.english.setdefault(row["id"], row["translated"])
                lex.english_summary[row["id"]] = row["summary"]
        if labeled:
            for row in labeled:
                lex.danish.setdefault(row["id"], row["body"])
                lex.danish_summary[row["id"]] = row["summary"]
        return lex


def mock_mark(direction: str, text: str) -> str:
    return f"[{direction}] {text}"


def translate_article(row_id: str, danish: str, lexicon: HopLexicon) -> str:
    """DA→EN hop. Prefer the fixture; otherwise mark the Danish text."""
    if row_id in lexicon.english:
        return lexicon.english[row_id]
    return mock_mark("da→en", danish)


def summarize_english(row_id: str, english: str, lexicon: HopLexicon, *, lead_sentences: int = 1) -> str:
    """English compression hop. Prefer the fixture; else lead-N."""
    if row_id in lexicon.english_summary:
        return lexicon.english_summary[row_id]
    sentences = split_sentences(english)
    if not sentences:
        return mock_mark("en-sum", english)
    return " ".join(sentences[:lead_sentences])


def translate_summary_back(row_id: str, english_summary: str, lexicon: HopLexicon) -> str:
    """EN→DA hop on the *summary*, matching `translate_back.py`."""
    if row_id in lexicon.danish_summary:
        return lexicon.danish_summary[row_id]
    return mock_mark("en→da", english_summary)


def aligned_sentence_pairs(row_id: str, lexicon: HopLexicon) -> list[tuple[str, str]]:
    """Zip Danish / English sentences when counts match.

    The fictional fixtures were written with matching sentence counts so
    a pack report can show hop 1 at sentence granularity. If the counts
    diverge, return a single pair (whole article, whole translation).
    """
    danish = lexicon.danish.get(row_id, "")
    english = lexicon.english.get(row_id, "")
    da_sents = split_sentences(danish)
    en_sents = split_sentences(english)
    if da_sents and len(da_sents) == len(en_sents):
        return list(zip(da_sents, en_sents))
    if danish or english:
        return [(danish, english)]
    return []


def lead_n_danish(danish: str, n: int = 1) -> str:
    """Cheap extractive baseline: first `n` Danish sentences."""
    sentences = split_sentences(danish)
    if not sentences:
        return ""
    return " ".join(sentences[:n])
