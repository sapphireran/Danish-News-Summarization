"""Sentence packing used by the 2023 translation and summarization scripts.

`translate.py` and `summary.py` both:

1. sentence-split an article
2. force-split any sentence whose measured length exceeds a budget
3. pack the pieces into windows that stay under `0.9 * 512` tokens

The course files count *tokens* when deciding whether a sentence is too
long, but `split_long_sentence` itself counts *characters* (`len(word)+1`).
This module keeps that quirk so the examples stay honest, and also exposes
a length function you can replace in tests.

NLTK is intentionally not imported. A small whitespace / punctuation
tokenizer stands in for `nltk.tokenize.word_tokenize` and `sent_tokenize`.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence

PUNCT_BREAK = {",", ";", ":"}
DEFAULT_MODEL_MAX = 512
DEFAULT_SAFETY = 0.9

LengthFn = Callable[[str], int]


def default_text_max_length(model_max: int = DEFAULT_MODEL_MAX, safety: float = DEFAULT_SAFETY) -> int:
    """Encoder budget used in translate.py / translate_back.py / summary.py."""
    return int(model_max * safety)


def simple_word_tokenize(text: str) -> list[str]:
    """Split words and peel off common punctuation as their own tokens."""
    tokens: list[str] = []
    current: list[str] = []
    for char in text:
        if char.isspace():
            if current:
                tokens.append("".join(current))
                current = []
        elif char in ",;:.!?\"“”'’()[]":
            if current:
                tokens.append("".join(current))
                current = []
            tokens.append(char)
        else:
            current.append(char)
    if current:
        tokens.append("".join(current))
    return tokens


def simple_sent_tokenize(text: str) -> list[str]:
    """Split on end punctuation plus whitespace. Keeps abbreviations imperfectly."""
    stripped = text.strip()
    if not stripped:
        return []
    parts = re.split(r"(?<=[.!?])\s+", stripped)
    return [part.strip() for part in parts if part.strip()]


def char_budget_len(text: str) -> int:
    """Approximate the course `split_long_sentence` running length.

    Each token contributes `len(token) + 1`, matching the `+ 1` space
    the original loop adds after every word_tokenize piece.
    """
    tokens = simple_word_tokenize(text)
    if not tokens:
        return 0
    return sum(len(token) + 1 for token in tokens)


def whitespace_len(text: str) -> int:
    """Fallback length: characters including spaces."""
    return len(text)


def split_long_sentence(sentence: str, max_length: int) -> list[str]:
    """Force-split one sentence the way `translate.py` does.

    The original loop flushes a chunk whenever it sees `,` / `;` / `:`
    *and* the running character budget is still below `max_length`. That
    is more aggressive than “split only when over budget”. This copy
    keeps the same rule so demos do not hide it.
    """
    words = simple_word_tokenize(sentence)
    current_chunk: list[str] = []
    chunks: list[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in PUNCT_BREAK and current_length < max_length:
            chunks.append(_join_tokens(current_chunk))
            current_chunk = []
            current_length = 0
        elif current_length >= max_length:
            last_word = current_chunk.pop()
            if current_chunk:
                chunks.append(_join_tokens(current_chunk))
            current_chunk = [last_word]
            current_length = len(last_word) + 1

    if current_chunk:
        chunks.append(_join_tokens(current_chunk))
    return chunks


def _join_tokens(tokens: Sequence[str]) -> str:
    """Join tokens and glue punctuation back onto the previous word."""
    if not tokens:
        return ""
    pieces: list[str] = [tokens[0]]
    for token in tokens[1:]:
        if token in ",;:.!?\"“”'’)]":
            pieces[-1] = pieces[-1] + token
        elif token in "([“\"":
            pieces.append(token)
        else:
            if pieces[-1] in "([“\"":
                pieces[-1] = pieces[-1] + token
            else:
                pieces.append(token)
    return " ".join(pieces)


def split_into_windows(
    article: str,
    text_max_length: int,
    length_fn: LengthFn | None = None,
    drop_empty: bool = True,
) -> list[list[str]]:
    """Pack sentences into encoder windows.

    `translate.py` can append an empty `current_list` when the first
    piece is already over budget. `drop_empty=True` (the example default)
    skips those empty windows. Pass `drop_empty=False` to study the
    original behaviour.
    """
    if length_fn is None:
        length_fn = char_budget_len

    raw_sentences = simple_sent_tokenize(article)
    pieces: list[tuple[str, int]] = []
    for sentence in raw_sentences:
        measured = length_fn(sentence)
        if measured > text_max_length:
            for chunk in split_long_sentence(sentence, text_max_length):
                pieces.append((chunk, length_fn(chunk)))
        else:
            pieces.append((sentence, measured))

    windows: list[list[str]] = []
    current_list: list[str] = []
    current_length = 0
    for sentence, length in pieces:
        if current_length + length > text_max_length:
            if current_list or not drop_empty:
                windows.append(current_list)
            current_list = [sentence]
            current_length = length
        else:
            current_list.append(sentence)
            current_length += length
    if current_list:
        windows.append(current_list)
    return windows


def windows_to_text(windows: Sequence[Sequence[str]]) -> list[str]:
    """Join each window the way `summary.py` does before T5."""
    return [" ".join(sentences) for sentences in windows]


def split_article(article: str, text_max_length: int, length_fn: LengthFn | None = None) -> list[str]:
    """Article → list of sub-articles that each fit `text_max_length`."""
    return windows_to_text(split_into_windows(article, text_max_length, length_fn=length_fn))


def window_stats(article: str, text_max_length: int, length_fn: LengthFn | None = None) -> dict[str, int]:
    """Tiny report used by demo_chunking and inspect tools."""
    if length_fn is None:
        length_fn = char_budget_len
    windows = split_into_windows(article, text_max_length, length_fn=length_fn)
    lengths = [length_fn(" ".join(window)) for window in windows]
    return {
        "sentences": len(simple_sent_tokenize(article)),
        "windows": len(windows),
        "max_window_len": max(lengths) if lengths else 0,
        "min_window_len": min(lengths) if lengths else 0,
        "chars": len(article),
    }
