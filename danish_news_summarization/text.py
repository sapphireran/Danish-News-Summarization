"""Small, dependency-free sentence and word tokenizers.

The 2023 project scripts call ``nltk.sent_tokenize`` / ``word_tokenize``.
Those are the right tools once NLTK's ``punkt`` models are installed.
Examples and unit tests use the helpers below so a laptop without NLTK
can still exercise the same chunking rules.
"""

from __future__ import annotations

import re
from typing import Iterable, List

# Common Danish and English abbreviations that should not end a sentence.
# The matcher is case-insensitive and accepts an optional trailing period.
_ABBREVIATIONS = {
    "bl.a",
    "ca",
    "dr",
    "dvs",
    "e.g",
    "etc",
    "f.eks",
    "fr",
    "hr",
    "i.e",
    "jf",
    "kl",
    "kr",
    "m.fl",
    "m.v",
    "mia",
    "mio",
    "mr",
    "mrs",
    "ms",
    "nr",
    "osv",
    "pga",
    "prof",
    "skt",
    "st",
    "t.eks",
}

_ABBREV_RE = re.compile(
    r"\b(" + "|".join(re.escape(item) for item in sorted(_ABBREVIATIONS, key=len, reverse=True)) + r")\.",
    flags=re.IGNORECASE,
)

_WORD_RE = re.compile(r"\w+|[^\w\s]", flags=re.UNICODE)

# Split after ., !, or ? when the next visible character looks like a new sentence.
_SENTENCE_SPLIT_RE = re.compile(
    r"(?<=[.!?])\s+(?=[\"'«»“”]?[A-ZÆØÅ])"
)

_PLACEHOLDER = "§ABBREV{index}§"


def protect_abbreviations(text: str) -> str:
    """Replace known abbreviation periods so sentence splitting stays intact."""

    def _replace(match: re.Match[str]) -> str:
        return match.group(0)[:-1] + "\u2024"  # one-dot leader, not a terminator

    return _ABBREV_RE.sub(_replace, text)


def restore_abbreviations(text: str) -> str:
    """Undo :func:`protect_abbreviations`."""
    return text.replace("\u2024", ".")


def word_tokenize(sentence: str) -> List[str]:
    """Split a sentence into words and standalone punctuation tokens."""
    return [token for token in _WORD_RE.findall(sentence) if token.strip()]


def sent_tokenize(article: str) -> List[str]:
    """Split an article into sentences.

    Handles decimal commas (``2,4 millioner``), numeric thousands, and the
    abbreviation list above. This is intentionally conservative: a missed
    split only makes a chunk slightly longer, which the packer then splits.
    """
    if not article or not article.strip():
        return []

    normalized = protect_abbreviations(article.strip())
    normalized = re.sub(r"\s+", " ", normalized)
    parts = _SENTENCE_SPLIT_RE.split(normalized)
    sentences = [restore_abbreviations(part).strip() for part in parts if part.strip()]
    return sentences


def join_words(words: Iterable[str]) -> str:
    """Join word tokens with spaces, then glue punctuation back to the left."""
    pieces: List[str] = []
    for word in words:
        if pieces and re.fullmatch(r"[^\w\s]+", word) and word not in {"«", "“", "\""}:
            pieces[-1] = pieces[-1] + word
        else:
            if pieces:
                pieces.append(" " + word)
            else:
                pieces.append(word)
    return "".join(pieces)
