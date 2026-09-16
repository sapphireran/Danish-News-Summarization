"""Sentence packing that preserves the 2023 character-budget quirk.

``translate.py`` / ``summary.py`` packed windows with *model token* counts
from the OPUS-MT / T5 tokenizer, but the long-sentence fallback
(``split_long_sentence``) incremented ``current_length`` by ``len(word)+1``.
That is a character budget, not a token budget.

This module reimplements both paths without HuggingFace tokenizers so the
quirk can be demonstrated on a laptop.
"""

from __future__ import annotations

from dataclasses import dataclass

from .danish import split_sentences, word_tokenize


@dataclass(frozen=True)
class PackedWindow:
    index: int
    sentences: tuple[str, ...]
    char_len: int
    token_len: int

    @property
    def text(self) -> str:
        return " ".join(self.sentences)


def split_long_sentence(sentence: str, max_length: int) -> list[str]:
    """Faithful port of the 2023 ``split_long_sentence`` character splitter."""
    words = word_tokenize(sentence)
    current_chunk: list[str] = []
    chunks: list[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in {",", ";", ":"} and current_length < max_length:
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


def _join(tokens: list[str]) -> str:
    """Rejoin tokens, keeping punctuation tight against the previous word."""
    out: list[str] = []
    for tok in tokens:
        if not out:
            out.append(tok)
            continue
        if tok in {",", ";", ":", ".", "!", "?", "…"} or tok.startswith("'"):
            out[-1] = out[-1] + tok
        else:
            out.append(tok)
    return " ".join(out)


def pack_article(
    article: str,
    budget: int = 80,
    *,
    unit: str = "char",
    split_long: bool = True,
) -> list[PackedWindow]:
    """Greedy-pack sentences so each window stays under *budget*.

    Parameters
    ----------
    unit:
        ``"char"`` uses the 2023 long-sentence metric (``len(word)+1``).
        ``"token"`` uses whitespace/punctuation token counts — closer to
        what a real tokenizer budget was trying to approximate.
    """
    if budget < 8:
        raise ValueError("budget must be at least 8")
    if unit not in {"char", "token"}:
        raise ValueError("unit must be 'char' or 'token'")

    pieces: list[str] = []
    for sentence in split_sentences(article):
        measure = _measure(sentence, unit)
        if split_long and measure > budget:
            pieces.extend(split_long_sentence(sentence, budget))
        else:
            pieces.append(sentence)

    windows: list[list[str]] = []
    current: list[str] = []
    current_len = 0
    for piece in pieces:
        length = _measure(piece, unit)
        if current and current_len + length > budget:
            windows.append(current)
            current = [piece]
            current_len = length
        else:
            current.append(piece)
            current_len += length
    if current:
        windows.append(current)

    packed: list[PackedWindow] = []
    for i, sents in enumerate(windows):
        text = " ".join(sents)
        packed.append(
            PackedWindow(
                index=i,
                sentences=tuple(sents),
                char_len=sum(len(w) + 1 for w in word_tokenize(text)),
                token_len=len(word_tokenize(text)),
            )
        )
    return packed


def _measure(text: str, unit: str) -> int:
    tokens = word_tokenize(text)
    if unit == "token":
        return len(tokens)
    return sum(len(tok) + 1 for tok in tokens)
