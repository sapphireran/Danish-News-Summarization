"""Faithful reconstruction of the 2023 sentence-packing windows.

Two different length notions live in the original scripts, and they do
not agree:

* ``split_long_sentence`` in ``translate.py`` / ``summary.py`` accumulates
  ``len(word) + 1`` — a *character* budget — and cuts on ``,`` ``;`` ``:``
  or when the running length exceeds ``text_max_length``.
* ``split_into_sentences`` then packs those pieces using
  ``len(tokenizer.encode(sentence))`` — a *subword* budget.

``translate_back.py`` is sloppier still: it never splits a long sentence,
and it passes ``max_length`` (512) into a function parameter named
``text_max_length`` even though the module also computes
``text_max_length = int(512 * 0.9)``. The study kit exposes both
behaviours so the scar is visible instead of being "fixed" in silence.

Default ``text_max_length`` is ``int(512 * 0.9) == 460``, matching
``translate.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Protocol, Sequence

from .sentences import split_sentences
from .tokenize import join_tokens, tokenize_words

DEFAULT_MAX_LENGTH = 512
DEFAULT_TEXT_MAX_LENGTH = int(DEFAULT_MAX_LENGTH * 0.9)


class TokenCounter(Protocol):
    def count(self, text: str) -> int:
        """Return the budget consumed by ``text``."""


class WordTokenCounter:
    """One budget unit per word/number token. Punctuation is free.

    This is the laptop stand-in for ``len(tokenizer.encode(...))``. It
    under-counts relative to SentencePiece, which is the point: the kit
    never pretends to have OPUS-MT in memory.
    """

    def count(self, text: str) -> int:
        return sum(1 for tok in tokenize_words(text) if tok[0].isalnum())


class CharPlusOneCounter:
    """Matches ``split_long_sentence``'s running length in the 2023 code."""

    def count(self, text: str) -> int:
        words = tokenize_words(text)
        if not words:
            return 0
        return sum(len(word) + 1 for word in words)


class ApproxSubwordCounter:
    """Word count times a fudge factor, floored at 1 for non-empty text.

    OPUS-MT SentencePiece typically emits a bit more than one piece per
    Danish word. ``1.3`` is a study-kit guess, not a measurement.
    """

    def __init__(self, pieces_per_word: float = 1.3) -> None:
        if pieces_per_word <= 0:
            raise ValueError("pieces_per_word must be positive")
        self.pieces_per_word = pieces_per_word
        self._words = WordTokenCounter()

    def count(self, text: str) -> int:
        words = self._words.count(text)
        if words == 0:
            return 0
        return max(1, int(round(words * self.pieces_per_word)))


@dataclass(frozen=True)
class PackedWindow:
    """One translate/summarise call's worth of sentences."""

    sentences: List[str]
    token_budget: int

    @property
    def text(self) -> str:
        return " ".join(self.sentences)

    @property
    def n_sentences(self) -> int:
        return len(self.sentences)


def split_long_sentence(
    sentence: str,
    max_length: int,
    punct_cuts: Sequence[str] = (",", ";", ":"),
) -> List[str]:
    """Port of ``split_long_sentence`` from ``translate.py``.

    Length is ``len(word) + 1`` per token, *not* a model token count.
    Cuts prefer ``,`` ``;`` ``:`` while still under budget; otherwise the
    last word overflows into the next chunk.
    """
    if max_length <= 0:
        raise ValueError("max_length must be positive")
    words = tokenize_words(sentence)
    if not words:
        return []

    current_chunk: List[str] = []
    chunks: List[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in punct_cuts and current_length < max_length:
            chunks.append(join_tokens(current_chunk))
            current_chunk = []
            current_length = 0
        elif current_length >= max_length:
            last_word = current_chunk.pop()
            if current_chunk:
                chunks.append(join_tokens(current_chunk))
            current_chunk = [last_word]
            current_length = len(last_word) + 1

    if current_chunk:
        chunks.append(join_tokens(current_chunk))
    return chunks


def pack_pieces(
    pieces: Sequence[str],
    text_max_length: int,
    counter: TokenCounter,
) -> List[PackedWindow]:
    """Greedy pack of pre-split pieces, matching ``split_into_sentences``.

    A single piece longer than the budget becomes its own window. The
    2023 loop does the same: it starts a new list when the *next* piece
    would overflow, so an oversized piece sits alone rather than being
    re-split at this stage.
    """
    if text_max_length <= 0:
        raise ValueError("text_max_length must be positive")

    windows: List[PackedWindow] = []
    current: List[str] = []
    current_length = 0

    for piece in pieces:
        if not piece:
            continue
        length = counter.count(piece)
        if current and current_length + length > text_max_length:
            windows.append(PackedWindow(list(current), current_length))
            current = [piece]
            current_length = length
        else:
            current.append(piece)
            current_length += length

    if current:
        windows.append(PackedWindow(list(current), current_length))
    return windows


def flatten_sentences(
    article: str,
    text_max_length: int,
    counter: TokenCounter,
    split_oversized: bool = True,
) -> List[str]:
    """Sentence-split, then optionally char-budget-split long sentences."""
    raw = split_sentences(article)
    pieces: List[str] = []
    for sentence in raw:
        length = counter.count(sentence)
        if split_oversized and length > text_max_length:
            pieces.extend(split_long_sentence(sentence, text_max_length))
        else:
            pieces.append(sentence)
    return pieces


def pack_article(
    article: str,
    text_max_length: int = DEFAULT_TEXT_MAX_LENGTH,
    counter: TokenCounter | None = None,
    split_oversized: bool = True,
) -> List[PackedWindow]:
    """Pack an article the way ``translate.py`` does (default settings)."""
    used = counter or WordTokenCounter()
    pieces = flatten_sentences(
        article,
        text_max_length=text_max_length,
        counter=used,
        split_oversized=split_oversized,
    )
    return pack_pieces(pieces, text_max_length=text_max_length, counter=used)


def pack_like_translate_back(
    article: str,
    max_length: int = DEFAULT_MAX_LENGTH,
    counter: TokenCounter | None = None,
) -> List[PackedWindow]:
    """Reproduce ``translate_back.py``: no long-sentence split, budget 512."""
    used = counter or WordTokenCounter()
    pieces = flatten_sentences(
        article,
        text_max_length=max_length,
        counter=used,
        split_oversized=False,
    )
    return pack_pieces(pieces, text_max_length=max_length, counter=used)


def window_texts(windows: Sequence[PackedWindow]) -> List[str]:
    return [window.text for window in windows]


def packing_stats(windows: Sequence[PackedWindow]) -> dict:
    if not windows:
        return {
            "n_windows": 0,
            "n_sentences": 0,
            "mean_budget": 0.0,
            "max_budget": 0,
            "min_budget": 0,
        }
    budgets = [w.token_budget for w in windows]
    n_sents = sum(w.n_sentences for w in windows)
    return {
        "n_windows": len(windows),
        "n_sentences": n_sents,
        "mean_budget": sum(budgets) / len(budgets),
        "max_budget": max(budgets),
        "min_budget": min(budgets),
    }


# Kept for callers that want a function (not a class) as the counter.
def word_count(text: str) -> int:
    return WordTokenCounter().count(text)


CounterFactory = Callable[[], TokenCounter]
