"""Length-aware sentence batching used by the translation and summary steps.

OPUS-MT and the English news T5 checkpoint both sit near a 512-token window.
Danish news bodies are often longer than that, so the original course scripts
split each article into sentences, then pack those sentences into batches that
fit under a conservative fraction of the model limit.

This module keeps that behaviour in one place so the examples can show it
without loading CTranslate2 or Hugging Face weights.
"""

from __future__ import annotations

from typing import Callable, Iterable, List, Sequence

DEFAULT_MAX_LENGTH = 512
DEFAULT_TEXT_MAX_LENGTH_RATIO = 0.9
PUNCTUATION_SPLIT_MARKERS = {",", ";", ":"}


def text_max_length(
    max_length: int = DEFAULT_MAX_LENGTH,
    ratio: float = DEFAULT_TEXT_MAX_LENGTH_RATIO,
) -> int:
    """Return the working token budget used by the course scripts."""
    if max_length < 1:
        raise ValueError("max_length must be at least 1")
    if not 0 < ratio <= 1:
        raise ValueError("ratio must be in (0, 1]")
    return int(max_length * ratio)


def _default_length(text: str) -> int:
    """Fallback length function when a tokenizer is not available.

    Whitespace token count plus one special-token slot is a close enough
    stand-in for the examples. The course scripts pass Hugging Face
    ``tokenizer.encode`` lengths instead.
    """
    words = [part for part in text.split() if part]
    return len(words) + 1


def split_long_sentence(
    sentence: str,
    max_length: int,
    length_fn: Callable[[str], int] | None = None,
) -> List[str]:
    """Split an oversized sentence on commas or hard word boundaries.

    The original scripts measure length in characters while walking words,
    then re-encode the resulting chunks with the model tokenizer. The
    examples use the same walk so the demo output matches the course notes.
    """
    if max_length < 1:
        raise ValueError("max_length must be at least 1")

    words = sentence.split()
    if not words:
        return []

    current_chunk: List[str] = []
    chunks: List[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if _is_soft_break(word) and current_length < max_length:
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

    if length_fn is None:
        return chunks

    # Optional second pass: drop empty leftovers after a custom length check.
    return [chunk for chunk in chunks if length_fn(chunk) > 1 or chunk.strip()]


def split_into_sentence_batches(
    article: str,
    max_length: int = DEFAULT_MAX_LENGTH,
    ratio: float = DEFAULT_TEXT_MAX_LENGTH_RATIO,
    sentences: Sequence[str] | None = None,
    length_fn: Callable[[str], int] | None = None,
) -> List[List[str]]:
    """Pack article sentences into batches that stay under the token budget.

    Parameters
    ----------
    article:
        Full article text. Ignored when ``sentences`` is provided.
    max_length:
        Model context window. The working budget is ``int(max_length * ratio)``.
    ratio:
        Safety margin used by ``translate.py`` and ``summary.py``.
    sentences:
        Pre-split sentences. When omitted, the function splits on ``.!?``
        followed by whitespace, which is enough for the sample articles.
    length_fn:
        Callable that returns a length for one sentence. Defaults to a
        whitespace-token estimate.
    """
    budget = text_max_length(max_length, ratio)
    measure = length_fn or _default_length
    raw_sentences = list(sentences) if sentences is not None else _naive_sentences(article)

    sentence_tokens_lengths: List[tuple[str, int]] = []
    for sentence in raw_sentences:
        cleaned = sentence.strip()
        if not cleaned:
            continue
        length = measure(cleaned)
        if length > budget:
            for chunk in split_long_sentence(cleaned, budget, measure):
                sentence_tokens_lengths.append((chunk, measure(chunk)))
        else:
            sentence_tokens_lengths.append((cleaned, length))

    batches: List[List[str]] = []
    current_list: List[str] = []
    current_length = 0

    for sentence, length in sentence_tokens_lengths:
        if current_list and current_length + length > budget:
            batches.append(current_list)
            current_list = [sentence]
            current_length = length
        else:
            current_list.append(sentence)
            current_length += length

    if current_list:
        batches.append(current_list)

    return batches


def chunk_article(
    article: str,
    max_length: int = DEFAULT_MAX_LENGTH,
    ratio: float = DEFAULT_TEXT_MAX_LENGTH_RATIO,
    sentences: Sequence[str] | None = None,
    length_fn: Callable[[str], int] | None = None,
) -> List[str]:
    """Return packed sub-articles, one string per model window."""
    batches = split_into_sentence_batches(
        article,
        max_length=max_length,
        ratio=ratio,
        sentences=sentences,
        length_fn=length_fn,
    )
    return [" ".join(batch) for batch in batches]


def _is_soft_break(word: str) -> bool:
    """Return True when a word is, or ends with, a comma/semicolon/colon.

    NLTK ``word_tokenize`` emits punctuation as its own token. The examples
    use whitespace splits, so a trailing comma on ``del,`` must count too.
    """
    stripped = word.strip().rstrip("\"')]}»")
    if not stripped:
        return False
    if stripped in PUNCTUATION_SPLIT_MARKERS:
        return True
    return stripped[-1] in PUNCTUATION_SPLIT_MARKERS


def _naive_sentences(article: str) -> List[str]:
    """Tiny sentence splitter for examples that do not pull NLTK.

    NLTK ``punkt`` is what the course scripts use. The sample articles are
    written with clear ``.!?`` boundaries so this fallback stays readable.
    """
    if not article or not article.strip():
        return []

    sentences: List[str] = []
    current: List[str] = []
    for index, char in enumerate(article):
        current.append(char)
        if char in ".!?" and _looks_like_boundary(article, index):
            piece = "".join(current).strip()
            if piece:
                sentences.append(piece)
            current = []

    leftover = "".join(current).strip()
    if leftover:
        sentences.append(leftover)
    return sentences


def _looks_like_boundary(article: str, index: int) -> bool:
    if index + 1 >= len(article):
        return True
    nxt = article[index + 1]
    return nxt.isspace() or nxt in "\"')]}»"


def iter_chunks(articles: Iterable[str], **kwargs) -> Iterable[List[str]]:
    """Yield chunk lists for a stream of articles."""
    for article in articles:
        yield chunk_article(article, **kwargs)
