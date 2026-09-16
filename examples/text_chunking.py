"""Sentence packing used by translate.py and summary.py.

The original scripts talk to a Hugging Face tokenizer. The demos use
:class:`SimpleWordTokenizer` so a long article can be packed without
downloading SentencePiece models. The packing rules themselves follow
the 2023 code:

* sentences are accumulated until the next one would exceed the window
* leftover long sentences are broken on commas / semicolons / colons
  or on a running character budget
* each packed window is joined back into a string
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from examples.danish_sentences import sent_tokenize, word_tokenize


class Tokenizer(Protocol):
    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        ...


@dataclass(frozen=True)
class SimpleWordTokenizer:
    """A stand-in tokenizer that counts words plus a BOS/EOS pad of 2.

    This is *not* Marian or T5 sentencepiece. It exists so the packing
    demo can show the same control flow on CPU with zero downloads.
    Token ids are stable hashes, not a real vocabulary.
    """

    bos_eos_tokens: int = 2

    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        words = word_tokenize(text)
        ids = [(_stable_id(word) % 30_000) + 1 for word in words]
        if add_special_tokens:
            return [0] * self.bos_eos_tokens + ids
        return ids


def _stable_id(word: str) -> int:
    value = 0
    for char in word:
        value = (value * 31 + ord(char)) & 0xFFFFFFFF
    return value


def split_long_sentence(sentence: str, max_length: int) -> list[str]:
    """Break a long sentence on ``,`` / ``;`` / ``:`` or a word budget.

    ``max_length`` is treated as a *character* budget here, matching
    ``translate.py`` / ``summary.py``, which increment ``len(word) + 1``
    rather than tokenizer ids inside this helper.
    """
    words = word_tokenize(sentence)
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
    return chunks


def _join_words(words: list[str]) -> str:
    out: list[str] = []
    for word in words:
        if not out:
            out.append(word)
            continue
        if re_is_punct(word):
            out.append(word)
        else:
            out.append(" " + word)
    return "".join(out)


def re_is_punct(word: str) -> bool:
    return len(word) == 1 and not word.isalnum()


def split_into_sentences(
    article: str,
    text_max_length: int,
    tokenizer: Tokenizer,
) -> list[list[str]]:
    """Pack sentences into windows that stay under ``text_max_length`` ids."""
    raw_sentences = sent_tokenize(article)
    sentence_tokens_lengths: list[tuple[str, int]] = []

    for sentence in raw_sentences:
        tokens = tokenizer.encode(sentence, add_special_tokens=True)
        sentence_length = len(tokens)
        if sentence_length > text_max_length:
            for chunk in split_long_sentence(sentence, text_max_length):
                chunk_length = len(tokenizer.encode(chunk, add_special_tokens=True))
                sentence_tokens_lengths.append((chunk, chunk_length))
        else:
            sentence_tokens_lengths.append((sentence, sentence_length))

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
    tokenizer: Tokenizer | None = None,
) -> list[str]:
    """Split an article into sub-articles that fit ``text_max_length``."""
    if tokenizer is None:
        tokenizer = SimpleWordTokenizer()
    return sentences_to_text(
        split_into_sentences(article, text_max_length, tokenizer)
    )


@dataclass(frozen=True)
class PackedArticle:
    article_id: str
    windows: list[str]
    token_lengths: list[int]
    original_tokens: int


def pack_corpus(
    articles: list[tuple[str, str]],
    text_max_length: int,
    tokenizer: Tokenizer | None = None,
) -> list[PackedArticle]:
    """Pack ``(id, text)`` pairs and record per-window token counts."""
    if tokenizer is None:
        tokenizer = SimpleWordTokenizer()
    packed: list[PackedArticle] = []
    for article_id, text in articles:
        windows = split_article(text, text_max_length, tokenizer)
        packed.append(
            PackedArticle(
                article_id=article_id,
                windows=windows,
                token_lengths=[
                    len(tokenizer.encode(window, add_special_tokens=True))
                    for window in windows
                ],
                original_tokens=len(tokenizer.encode(text, add_special_tokens=True)),
            )
        )
    return packed
