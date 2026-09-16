"""Whitespace tokenizer that peels punctuation the way NLTK ``word_tokenize`` does.

The 2023 ``split_long_sentence`` helpers call ``nltk.word_tokenize``, then treat
``,``, ``;``, and ``:`` as flush points. A laptop walk-through should see the
same peel so the character-budget packer is comparable without downloading NLTK.
"""

from __future__ import annotations

import re
from typing import Iterable

# Leading / trailing marks NLTK typically splits off a word.
_LEAD = "([{«“‘'\""
_TRAIL = ")]}?!,;:.»”’'\""


def word_tokenize(text: str) -> list[str]:
    """Split *text* into words and lone punctuation tokens."""
    tokens: list[str] = []
    for raw in text.split():
        tokens.extend(_peel(raw))
    return tokens


def _peel(token: str) -> list[str]:
    lead: list[str] = []
    trail: list[str] = []
    body = token
    while body and body[0] in _LEAD:
        lead.append(body[0])
        body = body[1:]
    while body and body[-1] in _TRAIL:
        trail.append(body[-1])
        body = body[:-1]
    out: list[str] = []
    out.extend(lead)
    if body:
        # Keep internal hyphens and Danish letters on the word.
        out.append(body)
    out.extend(reversed(trail))
    return out


def approx_subword_len(text: str) -> int:
    """Rough mT5/OPUS piece count: short words stay 1, long compounds split.

    Used only as a *budget stand-in*. The 2023 scripts mix this idea with a
    character ``+ 1`` length inside ``split_long_sentence``.
    """
    n = 1  # special tokens
    for word in re.findall(r"\S+", text):
        letters = re.sub(r"[^\wæøåÆØÅ]", "", word, flags=re.UNICODE)
        if not letters:
            n += 1
            continue
        if len(letters) <= 4:
            n += 1
        else:
            n += 1 + (len(letters) - 4) // 4
    return n


def char_plus_one_len(tokens: Iterable[str]) -> int:
    """The 2023 running length: ``sum(len(word) + 1 for word in tokens)``."""
    return sum(len(word) + 1 for word in tokens)
