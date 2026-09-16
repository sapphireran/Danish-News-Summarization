"""Lightweight sentence and word tokenization for the toy examples.

The 2023 scripts call `nltk.sent_tokenize` and `nltk.word_tokenize` after
`nltk.download('punkt')`. That is fine on a lab machine and heavy for a
ten-row fixture. This module is a small, dependency-free stand-in that
behaves well on the fictional news in `examples/data/` and on ordinary
Danish/English period-space-capital boundaries.

It is not a replacement for Punkt. Abbreviations that are not in
`_ABBREVIATIONS` can still split wrongly. That is acceptable for the
examples; it is not acceptable for a 10k dump.
"""

from __future__ import annotations

import re

# Bare token (no trailing dot). Compared case-insensitively against the
# token *before* a period when we decide whether that period ends a sentence.
_ABBREVIATIONS = {
    "bl.a",
    "ca",
    "dr",
    "dvs",
    "etc",
    "f.eks",
    "frk",
    "fru",
    "hr",
    "iflg",
    "kl",
    "kr",
    "m.fl",
    "m.v",
    "mr",
    "mrs",
    "nr",
    "osv",
    "prof",
    "st",
    "t.ex",
}

# Words and single non-space punctuation, same grain as NLTK word_tokenize
# on the sample articles (punctuation is its own token).
_WORD_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)

def word_tokenize(text: str) -> list[str]:
    """Split `text` into words and punctuation tokens."""
    if not text:
        return []
    return _WORD_RE.findall(text)


def _is_abbreviation(token: str) -> bool:
    stripped = token.rstrip(".").lower()
    return stripped in _ABBREVIATIONS or token.lower() in _ABBREVIATIONS


def split_sentences(text: str) -> list[str]:
    """Split a paragraph into sentences.

    A period, exclamation mark, or question mark ends a sentence when it is
    followed by whitespace and then an uppercase letter (including ÆØÅ),
    and the token before the period is not a listed abbreviation or a
    number (so `4,2` and `kl. 12` stay intact).
    """
    if text is None:
        return []
    text = text.strip()
    if not text:
        return []

    sentences: list[str] = []
    start = 0
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]
        if ch in ".!?":
            # Consume a run of closing punctuation: `?"` or `...`
            j = i
            while j + 1 < n and text[j + 1] in '.!?"»”\'':
                j += 1
            rest = text[j + 1 :]
            if not rest.strip():
                break
            # Need whitespace then an uppercase starter.
            m = re.match(r"^(\s+)(\S)", rest)
            if not m:
                i += 1
                continue
            nxt = m.group(2)
            if not nxt[:1].isupper() and nxt[:1] not in "ÆØÅ":
                i += 1
                continue
            # Token immediately before the stopper.
            before = text[start:i].rstrip()
            last = before.split()[-1] if before.split() else ""
            if ch == "." and _is_abbreviation(last):
                i += 1
                continue
            end = j + 1
            piece = text[start:end].strip()
            if piece:
                sentences.append(piece)
            start = j + 1 + len(m.group(1))
            i = start
            continue
        i += 1

    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences
