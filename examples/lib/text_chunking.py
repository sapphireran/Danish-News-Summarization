"""Sentence packing used by translate.py, summary.py, and translate_back.py.

The course scripts each inlined a copy of this logic. This module keeps one
implementation so the CPU examples can print the same packs without loading
CTranslate2 or T5.

Length is measured in *tokenizer tokens* when a Hugging Face tokenizer is
passed in, otherwise in whitespace-separated words plus punctuation. The
word fallback is close enough to demo the packer; it will not match Marian
SentencePiece exactly.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence

_PUNCT_BREAKS = {",", ";", ":"}
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÆØÅ\"“])")
_WORD_SPLIT = re.compile(r"\w+|[^\w\s]", re.UNICODE)

LengthFn = Callable[[str], int]


def sent_tokenize_text(article: str, language: str = "danish") -> list[str]:
    """Split an article into sentences; prefer NLTK punkt when installed."""
    text = (article or "").strip()
    if not text:
        return []
    try:
        from nltk.tokenize import sent_tokenize

        return [s.strip() for s in sent_tokenize(text, language=language) if s.strip()]
    except Exception:
        parts = [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]
        return parts or [text]


def word_tokenize_text(sentence: str, language: str = "danish") -> list[str]:
    try:
        from nltk.tokenize import word_tokenize

        return word_tokenize(sentence, language=language)
    except Exception:
        return _WORD_SPLIT.findall(sentence)


def default_length_fn(text: str) -> int:
    """Stand-in for ``len(tokenizer.encode(text, add_special_tokens=True))``."""
    return max(1, len(word_tokenize_text(text)) + 2)


def make_tokenizer_length_fn(tokenizer) -> LengthFn:
    def _length(text: str) -> int:
        return len(tokenizer.encode(text, add_special_tokens=True))

    return _length


def split_long_sentence(
    sentence: str,
    max_length: int,
    *,
    length_fn: LengthFn | None = None,
    language: str = "danish",
) -> list[str]:
    """Cut an over-long sentence on words, preferring commas and colons.

    Mirrors ``split_long_sentence`` in translate.py / summary.py. The course
    code compared a running *character-ish* length (``len(word) + 1``) against
    a token budget, which is slightly inconsistent. Here the running budget
    uses the same ``length_fn`` as packing so a demo with ``max_length=40``
    is understandable. Pass ``legacy_char_budget=True`` via the wrapper
    below if you want the original mix of char counts vs token caps.
    """
    measure = length_fn or default_length_fn
    words = word_tokenize_text(sentence, language=language)
    if not words:
        return []
    if measure(sentence) <= max_length:
        return [sentence]

    current_chunk: list[str] = []
    chunks: list[str] = []

    def flush() -> None:
        if current_chunk:
            chunks.append(_join_words(current_chunk))
            current_chunk.clear()

    for word in words:
        tentative = current_chunk + [word]
        tentative_text = _join_words(tentative)
        tentative_len = measure(tentative_text)
        if word in _PUNCT_BREAKS and tentative_len < max_length:
            current_chunk.append(word)
            flush()
            continue
        if tentative_len >= max_length and current_chunk:
            flush()
            current_chunk.append(word)
            continue
        current_chunk.append(word)

    flush()
    return chunks or [sentence]


def split_long_sentence_legacy(sentence: str, max_length: int) -> list[str]:
    """Byte-for-byte control flow of the course ``split_long_sentence``.

    Uses ``len(word) + 1`` as the running length, compared against a token
    cap. Kept so the demo can show why a comma-split sometimes fires early.
    """
    words = word_tokenize_text(sentence)
    current_chunk: list[str] = []
    chunks: list[str] = []
    current_length = 0
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in _PUNCT_BREAKS and current_length < max_length:
            chunks.append(_join_words(current_chunk))
            current_chunk, current_length = [], 0
        elif current_length >= max_length:
            last_word = current_chunk.pop()
            chunks.append(_join_words(current_chunk))
            current_chunk, current_length = [last_word], len(last_word) + 1
    if current_chunk:
        chunks.append(_join_words(current_chunk))
    return chunks


def _join_words(words: Sequence[str]) -> str:
    out = []
    for i, word in enumerate(words):
        if i > 0 and not re.match(r"^[.,;:!?%)]+$", word) and words[i - 1] not in {"(", "[", "«"}:
            out.append(" ")
        out.append(word)
    return "".join(out)


def pack_sentences(
    sentence_lengths: Sequence[tuple[str, int]],
    max_length: int,
) -> list[list[str]]:
    """Greedy pack of (sentence, length) pairs into lists under ``max_length``."""
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


def split_into_sentence_packs(
    article: str,
    max_length: int,
    *,
    length_fn: LengthFn | None = None,
    language: str = "danish",
    split_overlong: bool = True,
    legacy_long_split: bool = False,
) -> list[list[str]]:
    """Full packer used conceptually by translate.py and summary.py.

    ``translate_back.py`` skips the over-long sentence splitter. Set
    ``split_overlong=False`` to mimic that script.
    """
    measure = length_fn or default_length_fn
    raw_sentences = sent_tokenize_text(article, language=language)
    sentence_tokens_lengths: list[tuple[str, int]] = []
    for sentence in raw_sentences:
        sentence_length = measure(sentence)
        if split_overlong and sentence_length > max_length:
            if legacy_long_split:
                pieces = split_long_sentence_legacy(sentence, max_length)
            else:
                pieces = split_long_sentence(
                    sentence, max_length, length_fn=measure, language=language
                )
            for chunk in pieces:
                sentence_tokens_lengths.append((chunk, measure(chunk)))
        else:
            sentence_tokens_lengths.append((sentence, sentence_length))
    return pack_sentences(sentence_tokens_lengths, max_length)


def split_article(
    article: str,
    max_length: int,
    *,
    length_fn: LengthFn | None = None,
    language: str = "english",
) -> list[str]:
    """Join each pack back into a sub-article (summary.py's ``split_article``)."""
    packs = split_into_sentence_packs(
        article, max_length, length_fn=length_fn, language=language
    )
    return [" ".join(sentences) for sentences in packs]


def pack_report(
    article: str,
    max_length: int,
    *,
    language: str = "danish",
    length_fn: LengthFn | None = None,
) -> dict:
    """Structured view for demos and length_stats.py."""
    measure = length_fn or default_length_fn
    packs = split_into_sentence_packs(
        article, max_length, length_fn=measure, language=language
    )
    pack_rows = []
    for i, pack in enumerate(packs, start=1):
        text = " ".join(pack)
        pack_rows.append(
            {
                "pack": i,
                "n_sentences": len(pack),
                "length": measure(text),
                "preview": text[:160].replace("\n", " "),
            }
        )
    return {
        "n_sentences": sum(len(p) for p in packs),
        "n_packs": len(packs),
        "max_length": max_length,
        "article_length": measure(article),
        "packs": pack_rows,
    }
