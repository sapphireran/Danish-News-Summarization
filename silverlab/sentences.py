"""Danish-aware sentence splitter used by the extractive baselines.

NLTK `punkt` is what `translate.py` and `summary.py` download at runtime. The
lab keeps a smaller, explicit abbreviation list so packing experiments do not
depend on a network fetch or a language model that was never committed.
"""

from __future__ import annotations

import re
from typing import List

# Surface forms as they appear in running Danish text, including the period.
# Longer strings are substituted first so "f.eks." is not eaten as "f." + "eks.".
# Titles and Latin shortenings are always protected, even before a capital
# ("Dr. Hansen"). Currency/percent marks are only protected when the next
# word is not a new sentence ("20 kr. stykket" vs "25 kr. Hallen åbner").
ALWAYS_ABBREVIATIONS = (
    "t.o.m.",
    "f.eks.",
    "bl.a.",
    "m.fl.",
    "m.m.",
    "osv.",
    "hhv.",
    "jvf.",
    "dvs.",
    "ift.",
    "pga.",
    "o.l.",
    "ca.",
    "nr.",
    "kl.",
    "dr.",
    "prof.",
    "pr.",
    "st.",
    "mv.",
)
ENDABLE_ABBREVIATIONS = (
    "kr.",
    "pct.",
)
ABBREVIATIONS = ALWAYS_ABBREVIATIONS + ENDABLE_ABBREVIATIONS

_ABBREV_PLACEHOLDER = "§ABBREV{0}§"
_DECIMAL_PLACEHOLDER = "§DEC{0}§"

# Split after . ! ? when the next visible word looks like a new sentence.
# Danish sentences start with a capital or an opening quote then a capital.
_SPLIT_RE = re.compile(
    r'(?<=[.!?])\s+(?=["«»“”‘’]?(?:[A-ZÆØÅ]))'
)

_DECIMAL_RE = re.compile(r"(?<=\d)\.(?=\d)")


def _protect(text: str) -> tuple[str, list[str], list[str]]:
    abbrev_bank: list[str] = []
    decimal_bank: list[str] = []
    protected = text
    for abbr in ALWAYS_ABBREVIATIONS + ENDABLE_ABBREVIATIONS:
        if abbr in ENDABLE_ABBREVIATIONS:
            needle = re.compile(
                re.escape(abbr) + r'(?!\s+["«»“”‘’]?(?:[A-ZÆØÅ]))',
                re.IGNORECASE,
            )
        else:
            needle = re.compile(re.escape(abbr), re.IGNORECASE)
        while True:
            match = needle.search(protected)
            if not match:
                break
            abbrev_bank.append(match.group(0))
            token = _ABBREV_PLACEHOLDER.format(len(abbrev_bank) - 1)
            protected = protected[: match.start()] + token + protected[match.end() :]

    def _stash_decimal(match: re.Match[str]) -> str:
        decimal_bank.append(match.group(0))
        return _DECIMAL_PLACEHOLDER.format(len(decimal_bank) - 1)

    protected = _DECIMAL_RE.sub(_stash_decimal, protected)
    return protected, abbrev_bank, decimal_bank


def _restore(text: str, abbrev_bank: list[str], decimal_bank: list[str]) -> str:
    restored = text
    for index, original in enumerate(decimal_bank):
        restored = restored.replace(_DECIMAL_PLACEHOLDER.format(index), original)
    for index, original in enumerate(abbrev_bank):
        restored = restored.replace(_ABBREV_PLACEHOLDER.format(index), original)
    return restored


def split_sentences(text: str) -> List[str]:
    """Split `text` into sentences. Blank input yields []."""
    if not text or not text.strip():
        return []
    protected, abbrevs, decimals = _protect(text.strip())
    parts = _SPLIT_RE.split(protected)
    sentences = []
    for part in parts:
        restored = _restore(part.strip(), abbrevs, decimals)
        if restored:
            sentences.append(restored)
    return sentences
