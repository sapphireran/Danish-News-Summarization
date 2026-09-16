"""Download-free token notions used by packing and length-inflation notes.

The 2023 scripts mix three different length ideas:

* ``translate.py`` / ``summary.py`` pack on *tokenizer* ids (OPUS / T5).
* ``split_long_sentence`` then breaks overflows using *whitespace words*
  and a running ``len(word) + 1`` counter that is closer to characters.
* ``translate_back.py`` packs on tokenizer ids but never splits a long
  sentence the way the forward hop does.

Examples in this repo cannot call SentencePiece, so the desk approximates
those notions with stdlib counters. They are intentionally crude: the point
is to see how a Danish compound and its English expansion disagree.
"""

from __future__ import annotations

import re
from enum import Enum

WORD_RE = re.compile(r"[0-9A-Za-zÆØÅæøåÉéÜüÖöÄä]+", re.UNICODE)
_SUBWORD_WIDTH = 4


class LengthNotion(str, Enum):
    WORDS = "words"
    CHARS = "chars"
    ROUGH_SUBWORD = "rough_subword"

    @property
    def label(self) -> str:
        return {
            LengthNotion.WORDS: "whitespace words (split_long_sentence-ish)",
            LengthNotion.CHARS: "characters including spaces",
            LengthNotion.ROUGH_SUBWORD: "rough 4-char pieces (BPE stand-in)",
        }[self]


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def rough_subwords(text: str) -> list[str]:
    """Split each word into fixed-width pieces.

    Danish compounds such as *færgeafgang* stay one word under ``words()``
    but become several pieces here, which is closer to what a multilingual
    SentencePiece model does to an unseen compound.
    """
    pieces: list[str] = []
    for word in words(text):
        if len(word) <= _SUBWORD_WIDTH:
            pieces.append(word)
            continue
        for index in range(0, len(word), _SUBWORD_WIDTH):
            pieces.append(word[index : index + _SUBWORD_WIDTH])
    return pieces


def measure(text: str, notion: LengthNotion) -> int:
    if notion is LengthNotion.WORDS:
        return len(words(text))
    if notion is LengthNotion.CHARS:
        return len(text)
    if notion is LengthNotion.ROUGH_SUBWORD:
        return len(rough_subwords(text))
    raise ValueError(f"unknown length notion: {notion}")


def char_word_counter(text: str) -> int:
    """Reproduce the 2023 ``len(word) + 1`` overflow counter."""
    return sum(len(word) + 1 for word in text.split())
