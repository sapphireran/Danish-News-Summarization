"""A small Danish sentence splitter for offline examples.

The 2023 course scripts call ``nltk.sent_tokenize`` (the English Punkt model)
on both Danish source text and English translations. That works well enough
for news prose, but it needs a downloaded NLTK resource and it is not aware
of common Danish abbreviations.

This module is intentionally dependency-free. It is good enough for the
sample articles in ``examples/data`` and for unit tests. It is not a full
linguistic tokenizer.
"""

from __future__ import annotations

import re

# Period-containing tokens that should not end a sentence.
# Keep the list conservative and news-oriented.
DANISH_ABBREVIATIONS = {
    "adr.",
    "ang.",
    "bl.a.",
    "ca.",
    "dr.",
    "dvs.",
    "etc.",
    "f.eks.",
    "frk.",
    "fru.",
    "hr.",
    "if.",
    "jf.",
    "kl.",
    "km.",
    "m.fl.",
    "m.m.",
    "mia.",
    "mio.",
    "nr.",
    "osv.",
    "pga.",
    "pr.",
    "prof.",
    "tlf.",
}

_ABBREV_PATTERN = re.compile(
    r"\b("
    + "|".join(
        re.escape(item.rstrip("."))
        for item in sorted(DANISH_ABBREVIATIONS, key=len, reverse=True)
    )
    + r")\.",
    flags=re.IGNORECASE,
)

_SENTENCE_END = re.compile(r"([.!?]+)(\s+|$)")
_INITIALS = re.compile(r"\b([A-ZÆØÅ])\.")
_ORDINALS = re.compile(r"\b(\d+)\.")


def _protect_abbreviations(text: str) -> tuple[str, dict[str, str]]:
    """Replace abbreviation periods with placeholders so they do not split."""
    placeholders: dict[str, str] = {}

    def replace_abbrev(match: re.Match[str]) -> str:
        token = match.group(0)
        key = f"[ABBREV{len(placeholders)}]"
        placeholders[key] = token
        return key

    def replace_initial(match: re.Match[str]) -> str:
        token = match.group(0)
        key = f"[INIT{len(placeholders)}]"
        placeholders[key] = token
        return key

    def replace_ordinal(match: re.Match[str]) -> str:
        token = match.group(0)
        key = f"[ORD{len(placeholders)}]"
        placeholders[key] = token
        return key

    protected = _ABBREV_PATTERN.sub(replace_abbrev, text)
    protected = _ORDINALS.sub(replace_ordinal, protected)
    protected = _INITIALS.sub(replace_initial, protected)
    return protected, placeholders


def _restore(text: str, placeholders: dict[str, str]) -> str:
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def split_danish_sentences(text: str) -> list[str]:
    """Split news-like Danish (or English) prose into sentences.

    Empty input returns an empty list. Whitespace-only fragments are dropped.
    A final fragment without terminal punctuation is kept if it has content.
    """
    if text is None:
        return []

    stripped = text.strip()
    if not stripped:
        return []

    protected, placeholders = _protect_abbreviations(stripped)
    sentences: list[str] = []
    start = 0

    for match in _SENTENCE_END.finditer(protected):
        end = match.end(1)
        piece = protected[start:end].strip()
        if piece:
            sentences.append(_restore(piece, placeholders))
        start = match.end()

    tail = protected[start:].strip()
    if tail:
        sentences.append(_restore(tail, placeholders))

    return sentences


def word_tokenize(text: str) -> list[str]:
    """Split text into words and standalone punctuation tokens.

    This mirrors the spirit of ``nltk.word_tokenize`` for the chunking
    examples without requiring NLTK. Contractions and hyphenated compounds
    stay attached.
    """
    if not text:
        return []
    return re.findall(r"\w+(?:[-']\w+)*|[^\w\s]", text, flags=re.UNICODE)
