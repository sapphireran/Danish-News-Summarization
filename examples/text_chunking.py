"""Sentence packing used by the 2023 translation / summarization scripts.

The course files copy-paste two slightly different versions of this logic.
This module is the version the offline examples run, with the original
behaviour preserved and a token-accurate splitter available for comparison.

It does not load Transformers or CTranslate2. Token counts come from a
callable ``tokenizer_len(text) -> int`` so a real Hugging Face tokenizer
can be swapped in later without changing the packer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Sequence, Tuple

# Punctuation the 2023 splitter treated as a "maybe cut here" mark.
SOFT_BREAKS = {",", ";", ":"}


TokenizerLen = Callable[[str], int]


def whitespace_tokenizer_len(text: str) -> int:
    """Cheap stand-in for a subword tokenizer.

    Counts whitespace-separated tokens after stripping. This is **not** the
    MarianMT or T5 vocabulary. It is good enough to exercise packing on the
    synthetic fixtures without downloading a model.
    """
    text = text.strip()
    if not text:
        return 0
    return len(text.split())


def character_len_plus_spaces(words: Sequence[str]) -> int:
    """Replicates the 2023 ``current_length += len(word) + 1`` accumulator."""
    if not words:
        return 0
    return sum(len(word) + 1 for word in words)


def simple_sent_tokenize(text: str) -> List[str]:
    """Minimal sentence splitter for the offline demos.

    NLTK ``punkt`` is what the course scripts call. This fallback splits on
    ``.``, ``!``, ``?`` followed by whitespace and an uppercase letter or
    Danish/English quote. It is intentionally conservative so fixtures stay
    predictable without downloading punkt.
    """
    if not text or not text.strip():
        return []

    sentences: List[str] = []
    start = 0
    i = 0
    n = len(text)
    terminals = {".", "!", "?"}

    while i < n:
        ch = text[i]
        if ch in terminals:
            # Skip common abbreviations that appear in the fixtures.
            window = text[max(0, i - 6) : i + 1].lower()
            if window.endswith(("bl.a.", "f.eks.", "ca.", "kr.", "dr.", "nr.")):
                i += 1
                continue
            j = i + 1
            while j < n and text[j] in {".", "!", "?", '"', "'", "”", "“"}:
                j += 1
            while j < n and text[j].isspace():
                j += 1
            if j >= n or text[j].isupper() or text[j] in {"«", "»", '"', "“"}:
                piece = text[start:i + 1].strip()
                if piece:
                    sentences.append(piece)
                start = j
                i = j
                continue
        i += 1

    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def word_tokenize(sentence: str) -> List[str]:
    """Split a sentence into words and standalone punctuation tokens."""
    tokens: List[str] = []
    buf: List[str] = []

    def flush() -> None:
        if buf:
            tokens.append("".join(buf))
            buf.clear()

    for ch in sentence:
        if ch.isspace():
            flush()
        elif ch in {",", ";", ":", ".", "!", "?", "(", ")", "«", "»", '"', "“", "”"}:
            flush()
            tokens.append(ch)
        else:
            buf.append(ch)
    flush()
    return tokens


def split_long_sentence_char_budget(
    sentence: str,
    max_length: int,
) -> List[str]:
    """Original 2023 helper: mix of character counts and a token-sized cap.

    ``max_length`` in the course scripts is a *token* budget (about 460),
    but the loop increments by character length. Examples keep that behaviour
    so the design note can be demonstrated rather than silently "fixed."
    """
    words = word_tokenize(sentence)
    current_chunk: List[str] = []
    chunks: List[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in SOFT_BREAKS and current_length < max_length:
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


def split_long_sentence_token_budget(
    sentence: str,
    max_length: int,
    tokenizer_len: TokenizerLen,
) -> List[str]:
    """Same cut points, but the budget is measured with ``tokenizer_len``."""
    words = word_tokenize(sentence)
    current_chunk: List[str] = []
    chunks: List[str] = []

    for word in words:
        trial = current_chunk + [word]
        trial_text = _join_words(trial)
        trial_len = tokenizer_len(trial_text)
        if word in SOFT_BREAKS and trial_len < max_length:
            chunks.append(trial_text)
            current_chunk = []
        elif trial_len >= max_length and current_chunk:
            chunks.append(_join_words(current_chunk))
            current_chunk = [word]
        else:
            current_chunk = trial

    if current_chunk:
        chunks.append(_join_words(current_chunk))
    return chunks


def _join_words(words: Sequence[str]) -> str:
    out: List[str] = []
    for word in words:
        if not out:
            out.append(word)
            continue
        if word in {",", ";", ":", ".", "!", "?"}:
            out[-1] = out[-1] + word
        else:
            out.append(word)
    return " ".join(out)


@dataclass(frozen=True)
class PackedArticle:
    """One article broken into model-sized sentence lists."""

    packs: Tuple[Tuple[str, ...], ...]
    token_lengths: Tuple[int, ...]

    @property
    def pack_count(self) -> int:
        return len(self.packs)

    def as_texts(self) -> List[str]:
        return [" ".join(pack) for pack in self.packs]


def pack_sentences(
    sentences: Iterable[str],
    text_max_length: int,
    tokenizer_len: TokenizerLen,
    *,
    split_overlong: bool = True,
    token_accurate_split: bool = False,
) -> PackedArticle:
    """Pack sentences into lists whose token lengths stay under the budget.

    Parameters
    ----------
    split_overlong:
        If True, sentences longer than ``text_max_length`` are split first
        (as in ``translate.py`` / ``summary.py``). ``translate_back.py``
        skipped this and assumed summaries were short.
    token_accurate_split:
        If True, over-long sentences use ``split_long_sentence_token_budget``.
        If False, use the original character-accumulator helper.
    """
    sentence_tokens_lengths: List[Tuple[str, int]] = []

    for sentence in sentences:
        length = tokenizer_len(sentence)
        if split_overlong and length > text_max_length:
            if token_accurate_split:
                pieces = split_long_sentence_token_budget(
                    sentence, text_max_length, tokenizer_len
                )
            else:
                pieces = split_long_sentence_char_budget(sentence, text_max_length)
            for piece in pieces:
                sentence_tokens_lengths.append((piece, tokenizer_len(piece)))
        else:
            sentence_tokens_lengths.append((sentence, length))

    sentence_lists: List[List[str]] = []
    current_list: List[str] = []
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

    packs = tuple(tuple(pack) for pack in sentence_lists)
    lengths = tuple(sum(tokenizer_len(s) for s in pack) for pack in packs)
    return PackedArticle(packs=packs, token_lengths=lengths)


def pack_article(
    article: str,
    text_max_length: int,
    tokenizer_len: TokenizerLen = whitespace_tokenizer_len,
    **kwargs,
) -> PackedArticle:
    """Sentence-tokenize ``article`` then pack it."""
    return pack_sentences(
        simple_sent_tokenize(article),
        text_max_length,
        tokenizer_len,
        **kwargs,
    )
