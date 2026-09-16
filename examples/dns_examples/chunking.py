"""Sentence packing as committed in `translate.py` / `summary.py` (Dec 2023).

Two different units live in the original helper:

- `split_long_sentence` walks **characters** (`len(word) + 1`) against a
  budget that the caller treats as a *token* limit (`int(512 * 0.9)`).
- The packer that builds `sentence_lists` adds **tokenizer lengths**.

This module keeps that split of responsibilities so the toy report can
show both. Pass a `TokenCounter` for packing and a `CharacterBudget` if
you want the 2023 long-sentence breaker unchanged.

`translate_back.py` never called `split_long_sentence`. Use
`pack_sentences(..., split_oversized=False)` to match that script.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, Sequence

from .sentences import word_tokenize as default_word_tokenize

WordTokenizer = Callable[[str], list[str]]


class TokenCounter(Protocol):
    """Something that can turn a string into a length the packer understands."""

    def count(self, text: str) -> int: ...


@dataclass(frozen=True)
class WhitespaceCounter:
    """Count whitespace-separated words, plus `special_tokens`.

    Close enough to a subword tokenizer on short news sentences that the
    packing demo is readable. Not a Marian length.
    """

    special_tokens: int = 2

    def count(self, text: str) -> int:
        words = [part for part in text.split() if part]
        if not words:
            return self.special_tokens
        return len(words) + self.special_tokens


@dataclass(frozen=True)
class CharacterBudget:
    """`len(text)` plus optional specials. Useful in unit tests."""

    special_tokens: int = 0

    def count(self, text: str) -> int:
        return len(text) + self.special_tokens


def split_long_sentence(
    sentence: str,
    max_length: int,
    word_tokenize: WordTokenizer = default_word_tokenize,
) -> list[str]:
    """Break one oversized sentence the way `translate.py` does.

    Length here is `sum(len(word) + 1 for word in current_chunk)`, i.e.
    characters plus a stand-in space, **not** model tokens.
    Soft breaks on `,` / `;` / `:` when the running length is still
    below `max_length`. Hard-breaks otherwise by popping the last word.
    """
    words = word_tokenize(sentence)
    current_chunk: list[str] = []
    chunks: list[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in [",", ";", ":"] and current_length < max_length:
            chunks.append(_join_words(current_chunk))
            current_chunk = []
            current_length = 0
        elif current_length >= max_length:
            last_word = current_chunk.pop()
            if current_chunk:
                chunks.append(_join_words(current_chunk))
            current_chunk = [last_word]
            current_length = len(last_word) + 1

    if current_chunk:
        chunks.append(_join_words(current_chunk))
    return [chunk for chunk in chunks if chunk]


def _join_words(words: Sequence[str]) -> str:
    """Join the way NLTK tokens look after `' '.join` in the 2023 scripts.

    That join puts a space before punctuation (`havnen .`). The toy
    pipeline keeps the quirk so a pack report is honest about the
    original helper, then `_clean_join` can tidy display text.
    """
    return " ".join(words)


def tidy_joined_tokens(text: str) -> str:
    """Undo the space-before-punctuation artefact of `' '.join(word_tokenize(...))`."""
    out = text
    for mark in [",", ";", ":", ".", "!", "?", ")", "]", "»", "”"]:
        out = out.replace(f" {mark}", mark)
    for mark in ["(", "[", "«", "“"]:
        out = out.replace(f"{mark} ", mark)
    return out


def pack_sentences(
    pieces: Sequence[str],
    max_length: int,
    counter: TokenCounter,
) -> list[list[str]]:
    """Greedy pack of already-cut pieces so each group's counted length ≤ budget.

    Matches the second loop in `translate.py` / `summary.py`:
    if adding the next piece would overflow, flush and start a new list.
    A single piece longer than the budget still becomes its own group
    (the 2023 code does the same after `split_long_sentence`).
    """
    groups: list[list[str]] = []
    current: list[str] = []
    current_length = 0

    for piece in pieces:
        length = counter.count(piece)
        if current and current_length + length > max_length:
            groups.append(current)
            current = [piece]
            current_length = length
        else:
            current.append(piece)
            current_length += length

    if current:
        groups.append(current)
    return groups


def split_into_sentence_groups(
    article: str,
    max_length: int,
    counter: TokenCounter,
    *,
    split_oversized: bool = True,
    word_tokenize: WordTokenizer = default_word_tokenize,
    sentence_split: Callable[[str], list[str]] | None = None,
) -> list[list[str]]:
    """Full 2023 pre-translate / pre-summarize cut.

    1. Sentence split.
    2. Optionally break sentences whose *counter* length exceeds `max_length`
       with `split_long_sentence` (character walker, original units).
    3. Pack remaining pieces by `counter`.
    """
    from .sentences import split_sentences as default_split

    splitter = sentence_split or default_split
    raw = splitter(article)
    pieces: list[str] = []
    for sentence in raw:
        if split_oversized and counter.count(sentence) > max_length:
            pieces.extend(split_long_sentence(sentence, max_length, word_tokenize))
        else:
            pieces.append(sentence)
    return pack_sentences(pieces, max_length, counter)


def groups_to_text(groups: Sequence[Sequence[str]]) -> list[str]:
    """`summary.py` `sentences_to_text`: join each group on a space."""
    return [" ".join(group) for group in groups]
