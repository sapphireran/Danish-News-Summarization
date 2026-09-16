"""Sentence packing used by translate.py / summary.py, without NLTK or models.

The 2023 scripts call ``nltk.tokenize.sent_tokenize`` and
``word_tokenize``, then pack encoded token lengths from a Hugging Face
tokenizer. This module keeps the same control flow so docs and tests can
show the algorithm on a laptop.

Token length is estimated with a callable. The default estimator counts
whitespace-separated tokens plus one, which is good enough to demonstrate
overflow behavior. Pass ``len(tokenizer.encode(text))`` in a real run.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Iterable, List, Sequence, Tuple

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WORD_SPLIT_RE = re.compile(r"\s+")
PUNCT_FLUSH = {",", ";", ":"}

LengthFn = Callable[[str], int]


def default_length(text: str) -> int:
    """Cheap stand-in for ``len(tokenizer.encode(text, add_special_tokens=True))``."""
    stripped = text.strip()
    if not stripped:
        return 1
    return len(stripped.split()) + 1


def split_sentences(article: str) -> List[str]:
    """Split on punctuation followed by whitespace.

    This is narrower than NLTK ``punkt`` (abbreviations will over-split)
    and is only for demos and tests.
    """
    text = " ".join(article.strip().split())
    if not text:
        return []
    parts = SENTENCE_SPLIT_RE.split(text)
    return [part.strip() for part in parts if part.strip()]


def split_long_sentence(
    sentence: str,
    max_length: int,
    length_fn: LengthFn | None = None,
) -> List[str]:
    """Split a long sentence on words, flushing at commas when still under budget.

    Mirrors ``split_long_sentence`` in ``translate.py`` and ``summary.py``.
    Those functions measure *character-ish* length with ``len(word) + 1`` while
    comparing against a *token* budget. This port uses ``length_fn`` for the
    overflow check so tests can inject a tokenizer. The comma flush still
    follows the original word loop.
    """
    if length_fn is None:
        length_fn = default_length

    words = [word for word in WORD_SPLIT_RE.split(sentence.strip()) if word]
    if not words:
        return []

    current_chunk: List[str] = []
    chunks: List[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in PUNCT_FLUSH and current_length < max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        elif current_length >= max_length:
            last_word = current_chunk.pop()
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [last_word]
            current_length = len(last_word) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # If a caller passed a real tokenizer, re-pack any leftover piece that
    # still encodes over the budget by falling back to raw word windows.
    repaired: List[str] = []
    for chunk in chunks:
        if length_fn(chunk) <= max_length or " " not in chunk:
            repaired.append(chunk)
            continue
        repaired.extend(_force_word_windows(chunk, max_length, length_fn))
    return repaired


def _force_word_windows(text: str, max_length: int, length_fn: LengthFn) -> List[str]:
    words = text.split()
    windows: List[str] = []
    start = 0
    while start < len(words):
        end = start + 1
        while end <= len(words) and length_fn(" ".join(words[start:end])) <= max_length:
            end += 1
        if end == start + 1:
            windows.append(words[start])
            start += 1
        else:
            windows.append(" ".join(words[start : end - 1]))
            start = end - 1
    return windows


def pack_sentences(
    sentences: Sequence[Tuple[str, int]],
    text_max_length: int,
) -> List[List[str]]:
    """Greedy pack of ``(sentence, length)`` pairs into lists under the budget."""
    sentence_lists: List[List[str]] = []
    current_list: List[str] = []
    current_length = 0

    for sentence, length in sentences:
        if current_list and current_length + length > text_max_length:
            sentence_lists.append(current_list)
            current_list = [sentence]
            current_length = length
        else:
            current_list.append(sentence)
            current_length += length

    if current_list:
        sentence_lists.append(current_list)
    return sentence_lists


def pack_article(
    article: str,
    text_max_length: int,
    length_fn: LengthFn | None = None,
) -> List[str]:
    """Return packed sub-articles, each intended to fit ``text_max_length``.

    This is the composition used before ``translate_batch`` / T5 generate:
    sentence split → optional long-sentence split → greedy pack → join.
    """
    if length_fn is None:
        length_fn = default_length

    measured: List[Tuple[str, int]] = []
    for sentence in split_sentences(article):
        length = length_fn(sentence)
        if length > text_max_length:
            for chunk in split_long_sentence(sentence, text_max_length, length_fn):
                measured.append((chunk, length_fn(chunk)))
        else:
            measured.append((sentence, length))

    packed = pack_sentences(measured, text_max_length)
    return [" ".join(group) for group in packed]


def iter_chunk_report(
    article: str,
    text_max_length: int,
    length_fn: LengthFn | None = None,
) -> Iterable[dict]:
    """Yield a small report dict per packed chunk (used by inspect_sample)."""
    if length_fn is None:
        length_fn = default_length
    for index, chunk in enumerate(pack_article(article, text_max_length, length_fn)):
        yield {
            "index": index,
            "length": length_fn(chunk),
            "budget": text_max_length,
            "fits": length_fn(chunk) <= text_max_length,
            "text": chunk,
        }
