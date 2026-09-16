"""Token-budget packing used by the 2023 translation and summary scripts.

``translate.py``, ``summary.py`` and ``translate_back.py`` all cut articles
into batches that fit a seq2seq maximum length (512 tokens, then a 90%
safety margin in the translation scripts). The logic is copy-pasted three
times in the course code.

This module reconstructs that algorithm so the examples can show it without
loading CTranslate2 or Hugging Face tokenizers.

Two length modes:

* ``historical`` — matches the 2023 ``split_long_sentence`` exactly,
  including the quirk that it flushes a chunk at *every* comma, semicolon
  or colon while the running character count is still under the limit.
* ``near_limit`` — only uses those punctuation marks as preferred split
  points once the chunk has reached ``punct_ratio * max_length``. This is
  what the comments in the original scripts appear to intend.

Length is measured by a caller-supplied ``length_fn``. The course scripts
mix two measures: character length while splitting an oversized sentence,
then tokenizer token counts while packing sentences into a batch. The
examples default to whitespace-aware word counts so they stay offline.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence

from .danish_sentences import split_danish_sentences, word_tokenize

LengthFn = Callable[[str], int]
PUNCT_SPLIT_MARKS = {",", ";", ":"}


def character_length(text: str) -> int:
    """Approximate the 2023 long-sentence counter (characters + spaces)."""
    return len(text)


def word_length(text: str) -> int:
    """Count word-like tokens; punctuation is ignored."""
    return sum(1 for token in word_tokenize(text) if token.isalnum() or any(ch.isalnum() for ch in token))


def split_long_sentence(
    sentence: str,
    max_length: int,
    length_fn: LengthFn = character_length,
    mode: str = "near_limit",
    punct_ratio: float = 0.6,
) -> list[str]:
    """Split one oversized sentence into smaller strings.

    Parameters
    ----------
    sentence:
        Source sentence that may exceed ``max_length``.
    max_length:
        Maximum accepted length for a chunk, in ``length_fn`` units.
    length_fn:
        Length measure. The original code uses ``len(word) + 1`` accumulated
        while scanning tokens, which is close to ``len(text)`` plus a trailing
        space. Using ``character_length`` is the closest offline stand-in.
    mode:
        ``historical`` or ``near_limit``.
    punct_ratio:
        Only used in ``near_limit`` mode.
    """
    if max_length <= 0:
        raise ValueError("max_length must be positive")
    if mode not in {"historical", "near_limit"}:
        raise ValueError("mode must be 'historical' or 'near_limit'")

    tokens = word_tokenize(sentence)
    if not tokens:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    punct_threshold = max(1, int(max_length * punct_ratio))

    def flush() -> None:
        nonlocal current, current_length
        if current:
            chunks.append(_join_tokens(current))
            current = []
            current_length = 0

    for token in tokens:
        tentative = current + [token]
        tentative_length = length_fn(_join_tokens(tentative))

        if mode == "historical":
            current = tentative
            current_length = tentative_length
            if token in PUNCT_SPLIT_MARKS and current_length < max_length:
                flush()
            elif current_length >= max_length:
                last = current.pop()
                if current:
                    chunks.append(_join_tokens(current))
                current = [last]
                current_length = length_fn(last)
            continue

        # near_limit: keep adding until we would exceed the budget, then
        # prefer the last punctuation in the current chunk if we are close.
        if tentative_length <= max_length:
            current = tentative
            current_length = tentative_length
            if token in PUNCT_SPLIT_MARKS and current_length >= punct_threshold:
                flush()
            continue

        if current:
            chunks.append(_join_tokens(current))
        current = [token]
        current_length = length_fn(token)
        if current_length > max_length:
            # Single token longer than the budget: emit it alone.
            flush()

    if current:
        chunks.append(_join_tokens(current))
    return chunks


def pack_units(
    units: Sequence[tuple[str, int]],
    max_length: int,
) -> list[list[str]]:
    """Pack ``(text, length)`` units into batches that stay under ``max_length``.

    This is the inner loop shared by ``split_into_sentences`` in
    ``translate.py`` / ``summary.py``. A unit that is itself longer than
    ``max_length`` starts a new batch on its own.
    """
    if max_length <= 0:
        raise ValueError("max_length must be positive")

    batches: list[list[str]] = []
    current: list[str] = []
    current_length = 0

    for text, length in units:
        if length < 0:
            raise ValueError("unit length cannot be negative")
        if current and current_length + length > max_length:
            batches.append(current)
            current = [text]
            current_length = length
        else:
            current.append(text)
            current_length += length

    if current:
        batches.append(current)
    return batches


def split_into_sentence_batches(
    article: str,
    max_length: int,
    length_fn: LengthFn = word_length,
    sentence_splitter: Callable[[str], list[str]] | None = None,
    mode: str = "near_limit",
) -> list[list[str]]:
    """Split an article, then pack sentences into model-sized batches.

    Oversized sentences are broken with ``split_long_sentence`` before packing,
    matching the course-script control flow.
    """
    splitter = sentence_splitter or split_danish_sentences
    raw_sentences = splitter(article)
    units: list[tuple[str, int]] = []

    for sentence in raw_sentences:
        length = length_fn(sentence)
        if length > max_length:
            for chunk in split_long_sentence(sentence, max_length, length_fn=length_fn, mode=mode):
                units.append((chunk, length_fn(chunk)))
        else:
            units.append((sentence, length))

    return pack_units(units, max_length)


def flatten_batches(batches: Iterable[Sequence[str]], separator: str = " ") -> list[str]:
    """Join each batch into a single string."""
    return [separator.join(batch) for batch in batches]


def _join_tokens(tokens: Sequence[str]) -> str:
    """Join word tokens and glue punctuation back onto the previous word."""
    parts: list[str] = []
    for token in tokens:
        if not parts:
            parts.append(token)
            continue
        if re_is_punct(token):
            parts[-1] = parts[-1] + token
        else:
            parts.append(token)
    return " ".join(parts)


def re_is_punct(token: str) -> bool:
    return bool(token) and not any(ch.isalnum() for ch in token)
