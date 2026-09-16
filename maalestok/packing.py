"""Faithful port of the 2023 sentence packer, plus a near-limit variant.

``translate.py`` / ``summary.py`` do two different length checks:

* ``split_long_sentence`` accumulates ``len(word) + 1`` (characters, plus a
  space) and flushes on ``,`` / ``;`` / ``:`` *before* the budget trips.
* ``split_into_sentences`` packs those chunks using ``tokenizer.encode``
  length (subwords), with ``text_max_length = int(512 * 0.9)`` for OPUS-MT
  and ``512`` for the English T5.

That mix is why a sentence that looks short in characters can still be
split, and why a comma mid-clause becomes a hard window boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .sentences import split_sentences
from .tokenize import approx_subword_len, char_plus_one_len, word_tokenize

LengthFn = Callable[[str], int]


@dataclass(frozen=True)
class PackedWindow:
    index: int
    text: str
    char_plus_one: int
    approx_tokens: int
    flushed_on_punct: bool


def split_long_sentence(sentence: str, max_length: int) -> list[str]:
    """Reproduce the 2023 character-budget splitter, including comma flush."""
    words = word_tokenize(sentence)
    current_chunk: list[str] = []
    chunks: list[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in [",", ";", ":"] and current_length < max_length:
            chunks.append(_join(current_chunk))
            current_chunk = []
            current_length = 0
        elif current_length >= max_length:
            last_word = current_chunk.pop()
            if current_chunk:
                chunks.append(_join(current_chunk))
            current_chunk = [last_word]
            current_length = len(last_word) + 1

    if current_chunk:
        chunks.append(_join(current_chunk))
    return chunks


def pack_article(
    article: str,
    *,
    budget: int = 460,
    length_fn: LengthFn | None = None,
    historical_long_split: bool = True,
) -> list[PackedWindow]:
    """Pack *article* into windows that stay under *budget*.

    When *historical_long_split* is true (default), overlong sentences are
    first cut with the 2023 character ``+ 1`` helper using the same *budget*.
    Packing then uses *length_fn* (approx subwords by default).
    """
    if length_fn is None:
        length_fn = approx_subword_len

    pieces: list[tuple[str, int, bool]] = []
    for sentence in split_sentences(article):
        token_len = length_fn(sentence)
        if historical_long_split and token_len > budget:
            for chunk in split_long_sentence(sentence, budget):
                flushed = chunk.rstrip().endswith((",", ";", ":"))
                pieces.append((chunk, length_fn(chunk), flushed))
        elif historical_long_split and char_plus_one_len(word_tokenize(sentence)) > budget:
            # The 2023 code checks *token* length first, but the long-split
            # helper itself is character-based. Mirror both gates.
            for chunk in split_long_sentence(sentence, budget):
                flushed = chunk.rstrip().endswith((",", ";", ":"))
                pieces.append((chunk, length_fn(chunk), flushed))
        else:
            pieces.append((sentence, token_len, False))

    windows: list[PackedWindow] = []
    current: list[str] = []
    current_len = 0
    flushed_any = False

    def flush() -> None:
        nonlocal current, current_len, flushed_any
        if not current:
            return
        text = " ".join(current).strip()
        windows.append(
            PackedWindow(
                index=len(windows),
                text=text,
                char_plus_one=char_plus_one_len(word_tokenize(text)),
                approx_tokens=length_fn(text),
                flushed_on_punct=flushed_any,
            )
        )
        current = []
        current_len = 0
        flushed_any = False

    for text, length, flushed in pieces:
        if current and current_len + length > budget:
            flush()
        current.append(text)
        current_len += length
        flushed_any = flushed_any or flushed
    flush()
    return windows


def _join(tokens: list[str]) -> str:
    """Join peeled tokens, gluing punctuation back onto the previous word."""
    if not tokens:
        return ""
    out = tokens[0]
    for tok in tokens[1:]:
        if tok in {",", ";", ":", ".", "!", "?", ")", "]", "»", "”", "’"}:
            out += tok
        elif out.endswith(("(", "[", "«", "“", "‘")):
            out += tok
        else:
            out += " " + tok
    return out
