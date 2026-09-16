"""Lightweight word tokenizer used instead of NLTK ``word_tokenize``.

The 2023 scripts call ``nltk.tokenize.word_tokenize`` inside
``split_long_sentence``. For the study kit we keep a small, deterministic
splitter that:

* treats Danish letters ``æøå`` as word characters
* peels off surrounding punctuation
* keeps decimal numbers and times (``3,5``, ``06.00``, ``12.000``) intact
* never requires a download

The goal is not byte-identical NLTK output. It is a stable, testable stand-in
so packing windows can be reasoned about without the Punkt model.
"""

from __future__ import annotations

import re
from typing import Iterable, List

# Letters: any Unicode letter. Danish needs æøå and also é (én, ét).
# A number token: 12 / 12.000 / 3,5 / 06.00 / 4.5
_NUMBER = r"\d+(?:[.,]\d+)*"

# A word: letters, optionally with internal hyphen (vest-jysk) or apostrophe.
_WORD = r"[^\W\d_]+(?:[-'][^\W\d_]+)*"

# Keep common symbols that the 2023 splitter treats as their own tokens
# because ``split_long_sentence`` looks for ',', ';' and ':' as cut points.
_PUNCT = r"[.,;:!?()\"«»'—–-]"

_TOKEN_RE = re.compile(rf"{_NUMBER}|{_WORD}|{_PUNCT}")

# Joiner used when we reconstruct a chunk. Matches the 2023 ``' '.join``.
JOIN = " "


def tokenize_words(text: str) -> List[str]:
    """Return word and punctuation tokens for ``text``."""
    if not text:
        return []
    return _TOKEN_RE.findall(text)


def join_tokens(tokens: Iterable[str]) -> str:
    """Join tokens the same way the 2023 long-sentence splitter does.

    That reconstruction is ugly around punctuation (``Havnen , sagde hun .``)
    — and that is intentional. The original ``split_long_sentence`` used
    ``' '.join(current_chunk)`` after ``word_tokenize``, so the study kit
    preserves the scar instead of silently cleaning it.
    """
    return JOIN.join(token for token in tokens if token != "")


def lowercase_words(text: str) -> List[str]:
    """Alphabetic tokens only, lowercased — used by ROUGE and lexicons."""
    return [tok.lower() for tok in tokenize_words(text) if _is_word(tok)]


def _is_word(token: str) -> bool:
    return bool(token) and (token[0].isalpha() or token[0].isdigit())


def count_words(text: str) -> int:
    """Count alphabetic/numeric tokens, ignoring bare punctuation."""
    return sum(1 for tok in tokenize_words(text) if _is_word(tok))
