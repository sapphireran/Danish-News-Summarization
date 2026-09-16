"""Sentence packing used by the DA↔EN translation and English summarization steps.

The original scripts in ``translate.py`` and ``summary.py`` pack articles into
windows that fit an encoder limit (512 tokens for OPUS-MT / T5-base). Those
scripts measure length with a Hugging Face tokenizer. This module keeps the
same packing algorithm but defaults to whitespace tokens so examples and unit
tests can run offline.

The character-vs-token mix in the 2023 scripts is preserved as a documented
quirk: ``split_long_sentence`` still walks characters (``len(word) + 1``),
while packing uses token counts. See ``docs/silver-label-pipeline.md``.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence

Sentence = str
TokenCounter = Callable[[str], int]

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÆØÅ\"“«])")
_ABBREVIATIONS = (
    "hr.",
    "fr.",
    "dr.",
    "prof.",
    "ca.",
    "bl.a.",
    "f.eks.",
    "dvs.",
    "m.fl.",
    "osv.",
    "kl.",
    "nr.",
)


def whitespace_token_count(text: str) -> int:
    """Count whitespace-separated tokens, treating punctuation as its own token."""
    if not text or not text.strip():
        return 0
    return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))


def simple_sent_tokenize(text: str) -> list[str]:
    """Regex sentence splitter with a short Danish/English abbreviation list.

    The original pipeline uses ``nltk.sent_tokenize``. Examples use this
    fallback so a laptop without NLTK data can still walk the algorithm.
    """
    if not text or not text.strip():
        return []

    protected = text
    placeholders: list[tuple[str, str]] = []
    for index, abbr in enumerate(_ABBREVIATIONS):
        token = f"__ABBR{index}__"
        if abbr in protected.lower():
            pattern = re.compile(re.escape(abbr), re.IGNORECASE)
            if pattern.search(protected):
                protected = pattern.sub(token, protected)
                placeholders.append((token, abbr))

    parts = [part.strip() for part in _SENTENCE_SPLIT.split(protected) if part.strip()]
    if not parts:
        parts = [protected.strip()]

    restored: list[str] = []
    for part in parts:
        for token, abbr in placeholders:
            part = part.replace(token, abbr)
        restored.append(part)
    return restored


def split_long_sentence(sentence: str, max_length: int) -> list[str]:
    """Split an over-budget sentence on punctuation, then on word boundaries.

    Mirrors ``translate.py`` / ``summary.py``: length is characters
    (``len(word) + 1``), not model tokens.
    """
    words = re.findall(r"\w+|[^\w\s]", sentence, flags=re.UNICODE)
    if not words:
        return []

    current_chunk: list[str] = []
    chunks: list[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in {",", ";", ":"} and current_length < max_length:
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
    text = " ".join(words)
    return re.sub(r"\s+([,.;:!?])", r"\1", text).strip()


def pack_sentences(
    sentence_lengths: Sequence[tuple[str, int]],
    max_length: int,
) -> list[list[str]]:
    """Greedy-pack (sentence, length) pairs into windows that stay under ``max_length``."""
    sentence_lists: list[list[str]] = []
    current_list: list[str] = []
    current_length = 0

    for sentence, length in sentence_lengths:
        if current_list and current_length + length > max_length:
            sentence_lists.append(current_list)
            current_list = [sentence]
            current_length = length
        else:
            current_list.append(sentence)
            current_length += length

    if current_list:
        sentence_lists.append(current_list)
    return sentence_lists


def split_into_sentences(
    article: str,
    text_max_length: int,
    count_tokens: TokenCounter | None = None,
    sent_tokenize: Callable[[str], list[str]] | None = None,
) -> list[list[str]]:
    """Split an article into sentence windows under ``text_max_length`` tokens."""
    counter = count_tokens or whitespace_token_count
    tokenize_sents = sent_tokenize or simple_sent_tokenize
    raw_sentences = tokenize_sents(article)
    sentence_tokens_lengths: list[tuple[str, int]] = []

    for sentence in raw_sentences:
        sentence_length = counter(sentence)
        if sentence_length > text_max_length:
            for chunk in split_long_sentence(sentence, text_max_length):
                sentence_tokens_lengths.append((chunk, counter(chunk)))
        else:
            sentence_tokens_lengths.append((sentence, sentence_length))

    return pack_sentences(sentence_tokens_lengths, text_max_length)


def split_article(
    article: str,
    text_max_length: int = 512,
    count_tokens: TokenCounter | None = None,
    sent_tokenize: Callable[[str], list[str]] | None = None,
) -> list[str]:
    """Return sub-articles that each fit the encoder window."""
    windows = split_into_sentences(
        article,
        text_max_length=text_max_length,
        count_tokens=count_tokens,
        sent_tokenize=sent_tokenize,
    )
    return [" ".join(sentences) for sentences in windows if sentences]


def describe_windows(
    article: str,
    text_max_length: int = 512,
    count_tokens: TokenCounter | None = None,
) -> list[dict[str, int | str]]:
    """Return per-window diagnostics used by the example walkthrough scripts."""
    counter = count_tokens or whitespace_token_count
    windows = split_article(article, text_max_length=text_max_length, count_tokens=counter)
    rows: list[dict[str, int | str]] = []
    for index, window in enumerate(windows):
        rows.append(
            {
                "window_index": index,
                "token_count": counter(window),
                "char_count": len(window),
                "sentence_count": len(simple_sent_tokenize(window)),
                "preview": window[:160].replace("\n", " "),
            }
        )
    return rows
