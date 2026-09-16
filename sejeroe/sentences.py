"""Sentence splitting that does not download NLTK ``punkt``.

The 2023 scripts call ``nltk.sent_tokenize`` after ``nltk.download('punkt')``.
That is fine on a GPU box and awkward in a docs checkout. This splitter is
narrow: it protects a closed list of abbreviations and decimal numbers, then
cuts on ``.!?`` followed by whitespace and a capital letter or opening quote.
"""

from __future__ import annotations

import re

# Periods in these tokens are not sentence boundaries.
ABBREVIATIONS = frozenset(
    {
        "f.eks",
        "bl.a",
        "ca",
        "dr",
        "hr",
        "fru",
        "fr",
        "nr",
        "kl",
        "osv",
        "m.fl",
        "m.m",
        "pga",
        "dvs",
        "d.v.s",
        "tlf",
        "km",
        "kr",
        "mio",
        "mia",
        "jf",
        "mr",
        "mrs",
        "ms",
        "e.g",
        "i.e",
        "vs",
        "etc",
        "no",
        "approx",
        "st",
        "jan",
        "feb",
        "mar",
        "apr",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    }
)

_ABBREV_PATTERN = re.compile(
    r"\b("
    + "|".join(re.escape(item) for item in sorted(ABBREVIATIONS, key=len, reverse=True))
    + r")\.",
    flags=re.IGNORECASE,
)
_DECIMAL = re.compile(r"(?<=\d)\.(?=\d)")
_ELLIPSIS = re.compile(r"\.\.\.")
# Danish news often opens a quote with » after a period; « is the closer.
_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-ZÆØÅ\"“«»])")
_SENTINEL = "<prd>"


def _protect(text: str) -> str:
    text = _ELLIPSIS.sub(_SENTINEL * 3, text)
    text = _DECIMAL.sub(_SENTINEL, text)
    return _ABBREV_PATTERN.sub(lambda match: match.group(1) + _SENTINEL, text)


def _restore(text: str) -> str:
    return text.replace(_SENTINEL, ".")


def split_sentences(text: str) -> list[str]:
    """Return stripped sentences, dropping empties."""
    compact = " ".join((text or "").split())
    if not compact:
        return []
    protected = _protect(compact)
    parts = _BOUNDARY.split(protected)
    return [_restore(part).strip() for part in parts if part.strip()]


def first_sentence(text: str) -> str:
    sentences = split_sentences(text)
    return sentences[0] if sentences else ""
