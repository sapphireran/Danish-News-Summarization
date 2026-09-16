"""Abbreviation-aware sentence splitting for the example demos.

The 2023 scripts call ``nltk.sent_tokenize``. This module is a small
stand-in so the examples run without NLTK, while still respecting the
Danish abbreviations that otherwise produce false splits
(``bl.a.``, ``f.eks.``, ``kl.``, and so on).
"""

from __future__ import annotations

import re

# Lowercased, without the trailing period. A match of ``token + '.'``
# inside a sentence is treated as an abbreviation, not a boundary.
DANISH_ABBREVIATIONS = {
    "bl.a",
    "f.eks",
    "fx",
    "m.fl",
    "m.v",
    "mv",
    "ca",
    "kr",
    "pct",
    "dr",
    "hr",
    "fru",
    "jf",
    "osv",
    "dvs",
    "hhv",
    "kl",
    "nr",
    "st",
    "s",
    "t",
    "ang",
    "evt",
    "ifm",
    "io",
    "mia",
    "mio",
    "phd",
    "km",
    "m",
    "cm",
}

_BOUNDARY = re.compile(r"([.!?]+)(\s+|$)")
_WORD_BEFORE = re.compile(r"([^\s.!?]+)$")


def _is_abbreviation(prefix: str) -> bool:
    match = _WORD_BEFORE.search(prefix.rstrip())
    if match is None:
        return False
    token = match.group(1).lower().rstrip(".")
    if token in DANISH_ABBREVIATIONS:
        return True
    # Initials: "M." / "A.P."
    if len(token) == 1 and token.isalpha():
        return True
    if token.count(".") >= 1 and all(part.isalpha() and len(part) <= 3 for part in token.split(".") if part):
        return True
    return False


def sent_tokenize(text: str) -> list[str]:
    """Split ``text`` into sentences.

    Periods that belong to :data:`DANISH_ABBREVIATIONS` or single-letter
    initials do not start a new sentence. Newlines are treated as
    whitespace. Empty input yields an empty list.
    """
    if not text or not text.strip():
        return []

    collapsed = re.sub(r"\s+", " ", text.strip())
    sentences: list[str] = []
    start = 0
    for match in _BOUNDARY.finditer(collapsed):
        prefix = collapsed[start : match.start()]
        if _is_abbreviation(prefix):
            continue
        end = match.end()
        sentence = collapsed[start:end].strip()
        if sentence:
            sentences.append(sentence)
        start = match.end()
    tail = collapsed[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def word_tokenize(text: str) -> list[str]:
    """Split on whitespace and isolate common punctuation as its own token."""
    if not text:
        return []
    pieces = re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)
    return pieces
