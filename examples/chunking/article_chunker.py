"""Sentence packing used by translate.py and summary.py.

The production scripts mix two length notions:

* packing uses tokenizer token counts (Marian / T5 encode length)
* split_long_sentence uses a character budget on NLTK word tokens

This module keeps that mix so a demo stays honest. Pass any object with
an ``encode(text, add_special_tokens=True) -> Sequence`` method as
``tokenizer``. ``WhitespaceApproxTokenizer`` is the CPU stand-in used
in the demo; it is *not* Marian or T5.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol, Sequence


class SupportsEncode(Protocol):
    def encode(self, text: str, add_special_tokens: bool = True) -> Sequence[int]:
        ...


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÆØÅ\"'(0-9])")
_PUNCT_BREAK = {",", ";", ":"}


class WhitespaceApproxTokenizer:
    """Cheap stand-in: one integer per whitespace token plus a BOS/EOS pad.

    Counts are in the same ballpark as a word-piece model on clean news
    prose, not a substitute for ``Helsinki-NLP/opus-mt-*`` or T5.
    """

    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        pieces = [part for part in re.split(r"\s+", text.strip()) if part]
        extra = 2 if add_special_tokens else 0
        return list(range(len(pieces) + extra))


def sent_tokenize(article: str) -> list[str]:
    """Split on punctuation + whitespace. Tries NLTK ``punkt`` first."""
    text = article.strip()
    if not text:
        return []
    try:
        import nltk
        from nltk.tokenize import sent_tokenize as nltk_sent_tokenize

        try:
            return nltk_sent_tokenize(text)
        except LookupError:
            nltk.download("punkt", quiet=True)
            return nltk_sent_tokenize(text)
    except ImportError:
        parts = _SENTENCE_SPLIT.split(text)
        return [part.strip() for part in parts if part.strip()]


def word_tokenize(sentence: str) -> list[str]:
    try:
        from nltk.tokenize import word_tokenize as nltk_word_tokenize

        return nltk_word_tokenize(sentence)
    except (ImportError, LookupError):
        return re.findall(r"\w+|[^\w\s]", sentence, flags=re.UNICODE)


def token_len(text: str, tokenizer: SupportsEncode) -> int:
    return len(tokenizer.encode(text, add_special_tokens=True))


def split_long_sentence(sentence: str, max_length: int) -> list[str]:
    """Character-budget splitter copied from translate.py / summary.py.

    ``max_length`` is treated as an approximate *character* budget
    (``len(word) + 1``), not a tokenizer token budget.
    """
    words = word_tokenize(sentence)
    current_chunk: list[str] = []
    chunks: list[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in _PUNCT_BREAK and current_length < max_length:
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
    return chunks


def split_into_sentences(
    article: str,
    text_max_length: int,
    tokenizer: SupportsEncode,
    *,
    split_overlong: bool = True,
) -> list[list[str]]:
    """Pack sentences into groups whose encode-lengths sum to <= limit.

    ``split_overlong=True`` matches ``translate.py`` / ``summary.py``.
    ``False`` matches ``translate_back.py`` (summaries only).
    """
    sentence_tokens_lengths: list[tuple[str, int]] = []
    for sentence in sent_tokenize(article):
        length = token_len(sentence, tokenizer)
        if split_overlong and length > text_max_length:
            for chunk in split_long_sentence(sentence, text_max_length):
                sentence_tokens_lengths.append((chunk, token_len(chunk, tokenizer)))
        else:
            sentence_tokens_lengths.append((sentence, length))

    sentence_lists: list[list[str]] = []
    current_list: list[str] = []
    current_length = 0
    for sentence, length in sentence_tokens_lengths:
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


def sentences_to_text(sentence_lists: list[list[str]]) -> list[str]:
    return [" ".join(sentences) for sentences in sentence_lists]


def split_article(
    article: str,
    text_max_length: int,
    tokenizer: SupportsEncode,
    *,
    split_overlong: bool = True,
) -> list[str]:
    """Return packed sub-articles, same contract as summary.split_article."""
    return sentences_to_text(
        split_into_sentences(
            article,
            text_max_length,
            tokenizer,
            split_overlong=split_overlong,
        )
    )


@dataclass(frozen=True)
class PackReport:
    article_chars: int
    article_approx_tokens: int
    n_source_sentences: int
    n_chunks: int
    chunk_token_lengths: list[int]
    chunk_char_lengths: list[int]
    chunks: list[str]


def report_pack(
    article: str,
    text_max_length: int,
    tokenizer: SupportsEncode | None = None,
    *,
    split_overlong: bool = True,
) -> PackReport:
    tokenizer = tokenizer or WhitespaceApproxTokenizer()
    chunks = split_article(
        article,
        text_max_length,
        tokenizer,
        split_overlong=split_overlong,
    )
    return PackReport(
        article_chars=len(article),
        article_approx_tokens=token_len(article, tokenizer),
        n_source_sentences=len(sent_tokenize(article)),
        n_chunks=len(chunks),
        chunk_token_lengths=[token_len(chunk, tokenizer) for chunk in chunks],
        chunk_char_lengths=[len(chunk) for chunk in chunks],
        chunks=chunks,
    )
