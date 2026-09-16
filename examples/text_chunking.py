"""GPU-free reimplementation of the 2023 sentence-packing helpers.

The control flow matches ``translate.py`` / ``summary.py``:

1. Sentence-tokenize the article.
2. Split any sentence whose *token* length exceeds ``text_max_length``.
3. Greedily pack (sentence, token_length) pairs into windows.

``split_long_sentence`` still uses the historical unit mismatch: it increments a
*character* budget (``len(word) + 1``) and compares it to a *token* cap. That is
intentional so demos stay honest about the course code.

The default tokenizer approximates SentencePiece with whitespace words plus one
special token. Swap in a Hugging Face tokenizer with the same ``encode``
signature when you debug real overflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Protocol, Sequence, Tuple

try:
    from nltk.tokenize import sent_tokenize, word_tokenize
except ImportError:  # pragma: no cover - exercised only in bare environments
    sent_tokenize = None
    word_tokenize = None


class Tokenizer(Protocol):
    def encode(self, text: str, add_special_tokens: bool = True) -> Sequence[int]:
        ...


class WhitespaceTokenizer:
    """Cheap stand-in: one whitespace word ≈ one token, plus an optional EOS."""

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        pieces = [p for p in text.split() if p]
        extra = 1 if add_special_tokens else 0
        return list(range(len(pieces) + extra))


def ensure_nltk() -> None:
    """Download punkt models if needed. Safe to call more than once."""
    if sent_tokenize is None or word_tokenize is None:
        raise ImportError(
            "nltk is required for examples.text_chunking. "
            "Install requirements-examples.txt."
        )
    import nltk

    for resource, path in (
        ("punkt", "tokenizers/punkt"),
        ("punkt_tab", "tokenizers/punkt_tab"),
    ):
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(resource, quiet=True)


def split_long_sentence(sentence: str, max_length: int) -> List[str]:
    """Split a long sentence on punctuation, then on a hard word cut.

    ``max_length`` is compared against a running *character* budget, matching
    the 2023 scripts.
    """
    if word_tokenize is None:
        raise ImportError("nltk.word_tokenize is unavailable")

    words = word_tokenize(sentence)
    current_chunk: List[str] = []
    chunks: List[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in [",", ";", ":"] and current_length < max_length:
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


def _join_words(words: Sequence[str]) -> str:
    """Join word-tokenizer output so Danish punctuation is not space-padded twice."""
    out: List[str] = []
    for word in words:
        if out and word in {",", ";", ":", ".", "!", "?", "%"}:
            out[-1] = out[-1] + word
        else:
            out.append(word)
    return " ".join(out)


def sentence_token_lengths(
    article: str,
    text_max_length: int,
    tokenizer: Tokenizer,
) -> List[Tuple[str, int]]:
    """Return (chunk, token_length) pairs after oversized-sentence splits."""
    if sent_tokenize is None:
        raise ImportError("nltk.sent_tokenize is unavailable")

    raw_sentences = sent_tokenize(article)
    pairs: List[Tuple[str, int]] = []
    for sentence in raw_sentences:
        tokens = tokenizer.encode(sentence, add_special_tokens=True)
        sentence_length = len(tokens)
        if sentence_length > text_max_length:
            for chunk in split_long_sentence(sentence, text_max_length):
                chunk_length = len(tokenizer.encode(chunk, add_special_tokens=True))
                pairs.append((chunk, chunk_length))
        else:
            pairs.append((sentence, sentence_length))
    return pairs


def pack_sentences(
    sentence_tokens_lengths: Sequence[Tuple[str, int]],
    text_max_length: int,
) -> List[List[str]]:
    """Greedy pack. A single item longer than the budget still gets its own list."""
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
    return sentence_lists


def split_into_sentence_packs(
    article: str,
    text_max_length: int,
    tokenizer: Tokenizer | None = None,
) -> List[List[str]]:
    """Full Stage-A/B/C pipeline used by the translation and summarization demos."""
    tokenizer = tokenizer or WhitespaceTokenizer()
    pairs = sentence_token_lengths(article, text_max_length, tokenizer)
    return pack_sentences(pairs, text_max_length)


def packs_to_windows(packs: Sequence[Sequence[str]]) -> List[str]:
    """Join each pack the way ``summary.py`` does before calling T5."""
    return [" ".join(sentences) for sentences in packs]


@dataclass
class PackTrace:
    """Debug view for the chunking demo."""

    article_id: str
    text_max_length: int
    pairs: List[Tuple[str, int]] = field(default_factory=list)
    packs: List[List[str]] = field(default_factory=list)

    @property
    def n_source_sentences(self) -> int:
        return len(self.pairs)

    @property
    def n_packs(self) -> int:
        return len(self.packs)

    def pack_token_sums(self, tokenizer: Tokenizer) -> List[int]:
        sums = []
        for pack in self.packs:
            total = 0
            for sentence in pack:
                total += len(tokenizer.encode(sentence, add_special_tokens=True))
            sums.append(total)
        return sums


def trace_article(
    article_id: str,
    article: str,
    text_max_length: int,
    tokenizer: Tokenizer | None = None,
) -> PackTrace:
    tokenizer = tokenizer or WhitespaceTokenizer()
    pairs = sentence_token_lengths(article, text_max_length, tokenizer)
    packs = pack_sentences(pairs, text_max_length)
    return PackTrace(
        article_id=article_id,
        text_max_length=text_max_length,
        pairs=pairs,
        packs=packs,
    )
