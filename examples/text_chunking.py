"""Dependency-free port of the article chunker used at labeling time.

``translate.py`` and ``summary.py`` sentence-split with NLTK ``punkt``,
measure each sentence in model tokens, and pack sentences into batches that
fit ``int(512 * 0.9)`` tokens. A single oversized sentence is broken by
``split_long_sentence``, which walks *words* and counts *characters* against
that same numeric budget.

This module keeps that mixed-unit behavior so the examples match the 2023
scripts, and also exposes a token-length callback so tests can inject a
fake encoder without downloading OPUS-MT or T5.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

# Same punctuation cut-points as translate.py / summary.py.
_SOFT_BREAKS = {",", ";", ":"}

# Tiny abbreviation list so a stdlib sentence splitter does not cut
# "f.eks. kommunen" or "dr. Hansen" the way raw ``split('.')`` would.
_ABBREVIATIONS = frozenset(
    {
        "hr",
        "fru",
        "dr",
        "ca",
        "bl.a",
        "bla",
        "f.eks",
        "fx",
        "osv",
        "etc",
        "kl",
        "nr",
        "st",
        "mr",
        "mrs",
        "ms",
    }
)

_WORD_RE = re.compile(r"\w+|[^\w\s]", flags=re.UNICODE)

EncodeFn = Callable[[str], int]


def default_encode_length(text: str) -> int:
    """Stand-in for ``len(tokenizer.encode(text))``.

    Counts whitespace-separated tokens and adds two for the special tokens
    OPUS-MT / T5 would attach. Good enough to demo packing; not a
    sentencepiece clone.
    """

    words = [part for part in text.split() if part]
    return len(words) + 2


def word_tokenize(text: str) -> list[str]:
    """Rough equivalent of NLTK ``word_tokenize`` for this chunker.

    Punctuation becomes its own token so the comma/semicolon rule can fire.
    """

    return _WORD_RE.findall(text)


def split_sentences(text: str) -> list[str]:
    """Lightweight sentence splitter for the example corpus.

    The root scripts use ``nltk.sent_tokenize``. This function is only for
    documentation runs: it splits on ``.!?`` followed by whitespace and an
    uppercase letter (or end of string), and refuses to split after a
    known abbreviation.
    """

    stripped = " ".join(text.split())
    if not stripped:
        return []

    pieces: list[str] = []
    start = 0
    for match in re.finditer(r"[.!?]", stripped):
        end = match.end()
        rest = stripped[end:]
        if rest and not re.match(r"\s", rest):
            continue
        lookahead = rest.lstrip()
        if lookahead and not lookahead[0].isupper():
            continue
        candidate = stripped[start:end].strip()
        token_before = re.search(r"([A-Za-zÆØÅæøå.]+)\s*$", stripped[: match.start()])
        head = token_before.group(1).rstrip(".").lower() if token_before else ""
        if head in _ABBREVIATIONS:
            continue
        if candidate:
            pieces.append(candidate)
        start = end
    tail = stripped[start:].strip()
    if tail:
        pieces.append(tail)
    return pieces


def split_long_sentence(
    sentence: str,
    max_length: int,
    *,
    length_unit: str = "chars",
    encode_fn: EncodeFn = default_encode_length,
) -> list[str]:
    """Mirror ``split_long_sentence`` from ``translate.py`` / ``summary.py``.

    ``length_unit="chars"`` is the original behavior: each word adds
    ``len(word) + 1`` to a running counter compared against ``max_length``.
    ``length_unit="tokens"`` uses ``encode_fn`` instead, which is what the
    surrounding packer already does for whole sentences.
    """

    words = word_tokenize(sentence)
    if not words:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    def piece_length(piece: Sequence[str]) -> int:
        joined = _join_words(piece)
        if length_unit == "tokens":
            return encode_fn(joined)
        return sum(len(word) + 1 for word in piece)

    for word in words:
        current.append(word)
        current_length = piece_length(current)
        if word in _SOFT_BREAKS and current_length < max_length:
            chunks.append(_join_words(current))
            current = []
            current_length = 0
        elif current_length >= max_length:
            last = current.pop()
            if current:
                chunks.append(_join_words(current))
            current = [last]
            current_length = piece_length(current)

    if current:
        chunks.append(_join_words(current))
    return chunks


def pack_sentences(
    sentences_with_lengths: Iterable[tuple[str, int]],
    text_max_length: int,
) -> list[list[str]]:
    """Greedy pack of ``(sentence, length)`` pairs under ``text_max_length``."""

    batches: list[list[str]] = []
    current: list[str] = []
    current_length = 0

    for sentence, length in sentences_with_lengths:
        if current and current_length + length > text_max_length:
            batches.append(current)
            current = [sentence]
            current_length = length
            continue
        current.append(sentence)
        current_length += length

    if current:
        batches.append(current)
    return batches


def sentence_token_lengths(
    article: str,
    text_max_length: int,
    encode_fn: EncodeFn = default_encode_length,
    *,
    long_sentence_unit: str = "chars",
) -> list[tuple[str, int]]:
    """Split an article and attach an encoder length to each piece."""

    measured: list[tuple[str, int]] = []
    for sentence in split_sentences(article):
        length = encode_fn(sentence)
        if length > text_max_length:
            for chunk in split_long_sentence(
                sentence,
                text_max_length,
                length_unit=long_sentence_unit,
                encode_fn=encode_fn,
            ):
                measured.append((chunk, encode_fn(chunk)))
        else:
            measured.append((sentence, length))
    return measured


def split_article(
    article: str,
    text_max_length: int,
    encode_fn: EncodeFn = default_encode_length,
    *,
    long_sentence_unit: str = "chars",
) -> list[str]:
    """Return packed sub-articles, each intended to fit ``text_max_length``."""

    measured = sentence_token_lengths(
        article,
        text_max_length,
        encode_fn,
        long_sentence_unit=long_sentence_unit,
    )
    batches = pack_sentences(measured, text_max_length)
    return [" ".join(batch) for batch in batches]


@dataclass(frozen=True)
class ChunkReport:
    article_id: str
    n_sentences: int
    n_chunks: int
    chunk_lengths: tuple[int, ...]
    chunks: tuple[str, ...]


def report_chunks(
    article_id: str,
    article: str,
    text_max_length: int,
    encode_fn: EncodeFn = default_encode_length,
) -> ChunkReport:
    chunks = split_article(article, text_max_length, encode_fn)
    return ChunkReport(
        article_id=article_id,
        n_sentences=len(split_sentences(article)),
        n_chunks=len(chunks),
        chunk_lengths=tuple(encode_fn(chunk) for chunk in chunks),
        chunks=tuple(chunks),
    )


def _join_words(words: Sequence[str]) -> str:
    """Join regex word tokens without a space before punctuation."""

    parts: list[str] = []
    for word in words:
        if parts and re.fullmatch(r"[^\w\s]+", word, flags=re.UNICODE):
            parts[-1] = parts[-1] + word
        elif parts:
            parts.append(" " + word)
        else:
            parts.append(word)
    return "".join(parts)
