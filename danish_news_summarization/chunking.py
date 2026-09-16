"""Article chunking used by translate.py, summary.py, and translate_back.py.

OPUS-MT and the English T5 news summarizer both sit near a 512-token
context window. The original scripts therefore:

1. Sentence-split the article.
2. Split any single sentence that still exceeds the budget.
3. Pack consecutive sentences into windows that stay under the budget.

Those three steps are duplicated almost verbatim across the root scripts.
This module is the shared implementation, with a pluggable length function
so examples can run on whitespace counts while the GPU scripts keep using
a Hugging Face tokenizer.
"""

from __future__ import annotations

from typing import Callable, Iterable, List, Protocol, Sequence, Tuple

from .text import join_words, sent_tokenize, word_tokenize

LengthFn = Callable[[str], int]


class TokenizerLike(Protocol):
    """Minimal surface used by the 2023 scripts: ``len(tokenizer.encode(text))``."""

    def encode(self, text: str, add_special_tokens: bool = True) -> Sequence[int]:
        ...


class WhitespaceTokenizer:
    """Stand-in tokenizer that counts whitespace words plus optional specials.

    Useful for examples and tests. It is *not* a substitute for the OPUS-MT
    or T5 tokenizers when you run the real models: subword counts are higher
    than whitespace counts, especially for Danish compounds.
    """

    def __init__(self, special_tokens: int = 2) -> None:
        self.special_tokens = special_tokens

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        words = text.split()
        extra = self.special_tokens if add_special_tokens else 0
        return [0] * (len(words) + extra)


def length_from_tokenizer(tokenizer: TokenizerLike) -> LengthFn:
    """Return a length function that mirrors ``len(tokenizer.encode(...))``."""

    def _length(text: str) -> int:
        return len(tokenizer.encode(text, add_special_tokens=True))

    return _length


def split_long_sentence(
    sentence: str,
    max_length: int,
    *,
    length_fn: LengthFn | None = None,
) -> List[str]:
    """Split a long sentence into smaller parts.

    Matches the original script behaviour: grow a chunk word by word, flush
    early at ``,``, ``;``, or ``:`` when still under the budget, and otherwise
    flush when the running character length meets ``max_length``.

    The optional ``length_fn`` is consulted *after* candidate chunks are
    built. If a flushed chunk still exceeds the token budget (common when
    ``max_length`` is a token limit but the original loop tracked
    characters), the chunk is split again on whitespace.
    """
    words = word_tokenize(sentence)
    if not words:
        return []

    current_chunk: List[str] = []
    chunks: List[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in [",", ";", ":"] and current_length < max_length:
            chunks.append(join_words(current_chunk))
            current_chunk, current_length = [], 0
        elif current_length >= max_length:
            last_word = current_chunk.pop()
            if current_chunk:
                chunks.append(join_words(current_chunk))
            current_chunk, current_length = [last_word], len(last_word) + 1

    if current_chunk:
        chunks.append(join_words(current_chunk))

    if length_fn is None:
        return [chunk for chunk in chunks if chunk.strip()]

    refined: List[str] = []
    for chunk in chunks:
        if length_fn(chunk) <= max_length:
            refined.append(chunk)
            continue
        refined.extend(_split_by_length_fn(chunk, max_length, length_fn))
    return [chunk for chunk in refined if chunk.strip()]


def _split_by_length_fn(text: str, max_length: int, length_fn: LengthFn) -> List[str]:
    """Last-resort split when a character-oriented chunk is still too many tokens."""
    words = text.split()
    chunks: List[str] = []
    current: List[str] = []
    for word in words:
        trial = (" ".join(current + [word])).strip()
        if current and length_fn(trial) > max_length:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        chunks.append(" ".join(current))
    return chunks


def pack_sentences_by_length(
    sentence_lengths: Sequence[Tuple[str, int]],
    max_length: int,
) -> List[List[str]]:
    """Pack ``(sentence, length)`` pairs into lists that stay under ``max_length``."""
    sentence_lists: List[List[str]] = []
    current_list: List[str] = []
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


def tokenize_sentences(
    article: str,
    max_length: int,
    length_fn: LengthFn,
    *,
    sentence_splitter: Callable[[str], List[str]] | None = None,
) -> List[Tuple[str, int]]:
    """Sentence-split an article and record a length for each (sub)sentence."""
    splitter = sentence_splitter or sent_tokenize
    raw_sentences = splitter(article)
    sentence_tokens_lengths: List[Tuple[str, int]] = []

    for sentence in raw_sentences:
        sentence_length = length_fn(sentence)
        if sentence_length > max_length:
            for chunk in split_long_sentence(sentence, max_length, length_fn=length_fn):
                sentence_tokens_lengths.append((chunk, length_fn(chunk)))
        else:
            sentence_tokens_lengths.append((sentence, sentence_length))
    return sentence_tokens_lengths


def split_into_sentences(
    article: str,
    max_length: int,
    tokenizer: TokenizerLike,
    *,
    sentence_splitter: Callable[[str], List[str]] | None = None,
) -> List[List[str]]:
    """Split an article into lists of sentences, each list under ``max_length`` tokens."""
    length_fn = length_from_tokenizer(tokenizer)
    pairs = tokenize_sentences(
        article,
        max_length,
        length_fn,
        sentence_splitter=sentence_splitter,
    )
    return pack_sentences_by_length(pairs, max_length)


def sentences_to_text(sentence_lists: Iterable[Sequence[str]]) -> List[str]:
    """Join each packed sentence list into a single string."""
    return [" ".join(sentences) for sentences in sentence_lists]


def split_article(
    article: str,
    text_max_length: int,
    tokenizer: TokenizerLike,
    *,
    sentence_splitter: Callable[[str], List[str]] | None = None,
) -> List[str]:
    """Split an article into sub-articles that fit the model context window."""
    sentence_lists = split_into_sentences(
        article,
        text_max_length,
        tokenizer,
        sentence_splitter=sentence_splitter,
    )
    return sentences_to_text(sentence_lists)
