"""Danish-aware sentence splitter.

The 2023 scripts call ``nltk.sent_tokenize`` (Punkt, English model by
default). Danish news has a different abbreviation list and uses ``kl.``,
``f.eks.``, ``bl.a.`` heavily. This splitter is conservative on purpose:

* split on ``.`` ``!`` ``?`` when the next sentence starts with a capital
  or a digit, or when we hit end-of-text
* do not split after a known abbreviation
* do not split inside numbers or times (``3,5``, ``06.00``, ``12.000``)
* do not split on ellipsis ``...``

It is good enough to pack the Vesterklit gazette and to unit-test the
abbreviation table. It is not a general Danish tokenizer.
"""

from __future__ import annotations

import re
from typing import List, Sequence, Set

# Period-terminated abbreviations seen in the 2023-style municipal copy.
# Stored without the final period. Multi-part forms (f.eks, t.o.m) are
# matched as a suffix of the token immediately before the period.
ABBREVIATIONS: Set[str] = {
    "f.eks",
    "bl.a",
    "ca",
    "kr",
    "osv",
    "m.fl",
    "m.v",
    "dvs",
    "nr",
    "km",
    "mio",
    "mia",
    "pct",
    "dr",
    "prof",
    "hr",
    "fr",
    "kl",
    "jf",
    "ang",
    "evt",
    "pga",
    "pr",
    "t.o.m",
    "f.o.m",
    "etc",
    "d",  # "d. 16. marts"
    "jan",
    "feb",
    "mar",
    "apr",
    "jun",
    "jul",
    "aug",
    "sep",
    "okt",
    "nov",
    "dec",
}

_SPLIT_PUNCT = {".", "!", "?"}


def split_sentences(text: str, extra_abbreviations: Sequence[str] | None = None) -> List[str]:
    """Split ``text`` into sentences. Empty input yields an empty list."""
    if text is None:
        return []
    stripped = text.strip()
    if not stripped:
        return []

    abbrev = set(ABBREVIATIONS)
    if extra_abbreviations:
        abbrev.update(a.lower().rstrip(".") for a in extra_abbreviations)

    sentences: List[str] = []
    start = 0
    i = 0
    n = len(stripped)

    while i < n:
        ch = stripped[i]
        if ch in _SPLIT_PUNCT:
            if ch == "." and _is_ellipsis(stripped, i):
                i += 1
                continue
            if ch == "." and _period_is_internal(stripped, i):
                i += 1
                continue
            if ch == "." and _period_follows_abbreviation(stripped, start, i, abbrev):
                i += 1
                continue
            if _looks_like_sentence_end(stripped, i):
                piece = stripped[start : i + 1].strip()
                if piece:
                    sentences.append(piece)
                i += 1
                while i < n and stripped[i].isspace():
                    i += 1
                start = i
                continue
        i += 1

    tail = stripped[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def _is_ellipsis(text: str, i: int) -> bool:
    # True if this period is part of "..." (or longer).
    left = i > 0 and text[i - 1] == "."
    right = i + 1 < len(text) and text[i + 1] == "."
    return left or right


def _period_is_internal(text: str, i: int) -> bool:
    """True for 06.00, 12.000, A.P. (letter.letter) and trailing ordinals 16."""
    prev_ok = i > 0 and (text[i - 1].isdigit() or text[i - 1].isalpha())
    nxt = i + 1
    if nxt < len(text) and (text[nxt].isdigit() or text[nxt].isalpha()):
        return prev_ok
    # Danish ordinal dates written as "16." before a month name are handled
    # as abbreviations via the token "16" — not here. A bare "16." at the
    # end of a clause should split.
    return False


def _token_before_period(text: str, start: int, period_index: int) -> str:
    j = period_index
    while j > start and not text[j - 1].isspace():
        j -= 1
    return text[j:period_index]


def _period_follows_abbreviation(
    text: str, start: int, period_index: int, abbrev: Set[str]
) -> bool:
    token = _token_before_period(text, start, period_index)
    if not token:
        return False
    lowered = token.lower()
    if lowered in abbrev:
        return True
    # Multi-dot abbreviations: the token already contains dots ("f.eks").
    if lowered.rstrip(".") in abbrev:
        return True
    # Single-letter initials: "A." "P." — treat as abbreviation unless the
    # next non-space character looks like a new sentence *and* the initial
    # is not followed by another initial. We keep initials glued.
    if len(token) == 1 and token.isalpha():
        return True
    return False


def _looks_like_sentence_end(text: str, period_index: int) -> bool:
    nxt = period_index + 1
    if nxt >= len(text):
        return True
    while nxt < len(text) and text[nxt].isspace():
        nxt += 1
    if nxt >= len(text):
        return True
    ch = text[nxt]
    # New sentence: capital (including ÆØÅ) or an opening quote/digit.
    if ch.isupper() or ch.isdigit() or ch in "«\"'(":
        return True
    # Danish quotes sometimes wrap a continuation; be conservative.
    return False


def first_sentences(text: str, k: int) -> str:
    """Lead-``k`` baseline used by the extractive hop."""
    if k <= 0:
        return ""
    sents = split_sentences(text)
    return " ".join(sents[:k])


_WS_RE = re.compile(r"\s+")


def squeeze_ws(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()
