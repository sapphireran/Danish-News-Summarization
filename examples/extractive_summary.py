"""Tiny extractive summarizer used by the offline toy pipeline.

The course project generates *abstractive* labels by translating Danish
news to English, running ``mrm8488/t5-base-finetuned-summarize-news``, and
translating the summary back to Danish. That path needs converted OPUS
models and a GPU-sized T5.

This module is a stand-in that stays inside Danish and never calls a
neural model. The default ``hybrid`` strategy keeps the news lede and
adds a TF-IDF sentence from the rest of the article. That is the usual
extractive floor for newswire, and it lets the toy pipeline stay honest
about what it can and cannot demonstrate versus T5.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable

from .danish_sentences import split_danish_sentences, word_tokenize

# Function words frequent in Danish news prose. Not exhaustive.
DANISH_STOPWORDS = {
    "af",
    "aldrig",
    "alle",
    "alt",
    "andre",
    "at",
    "blev",
    "blive",
    "bliver",
    "da",
    "de",
    "dem",
    "den",
    "denne",
    "der",
    "deres",
    "det",
    "dette",
    "dig",
    "din",
    "dog",
    "du",
    "efter",
    "eller",
    "en",
    "end",
    "er",
    "et",
    "for",
    "fra",
    "før",
    "ham",
    "han",
    "hans",
    "har",
    "havde",
    "have",
    "hende",
    "hendes",
    "her",
    "hos",
    "hun",
    "hvad",
    "hvis",
    "hvor",
    "i",
    "ikke",
    "ind",
    "jeg",
    "jer",
    "jo",
    "kan",
    "kom",
    "kommer",
    "kun",
    "kunne",
    "man",
    "med",
    "meget",
    "men",
    "mere",
    "mig",
    "min",
    "mod",
    "når",
    "ned",
    "noget",
    "nogen",
    "nok",
    "nu",
    "og",
    "også",
    "om",
    "op",
    "os",
    "over",
    "på",
    "selv",
    "sig",
    "sin",
    "sine",
    "sit",
    "skal",
    "skulle",
    "som",
    "så",
    "til",
    "ud",
    "under",
    "var",
    "ved",
    "vi",
    "vil",
    "ville",
    "være",
    "været",
}


def normalize_token(token: str) -> str:
    return token.casefold()


def content_tokens(text: str, stopwords: Iterable[str] = DANISH_STOPWORDS) -> list[str]:
    stopped = {word.casefold() for word in stopwords}
    tokens: list[str] = []
    for token in word_tokenize(text):
        folded = normalize_token(token)
        if not any(ch.isalpha() for ch in folded):
            continue
        if folded in stopped:
            continue
        if len(folded) <= 1:
            continue
        tokens.append(folded)
    return tokens


def sentence_scores(sentences: list[str]) -> list[float]:
    """Score each sentence as the mean TF of its content words.

    Using the mean (not the sum) avoids always preferring the longest
    sentence. A sentence with no content words scores 0.
    """
    tokenized = [content_tokens(sentence) for sentence in sentences]
    counts = Counter(token for sentence in tokenized for token in sentence)
    if not counts:
        return [0.0] * len(sentences)

    # Mild IDF-style downweighting so a word that appears in every sentence
    # does not dominate. With tiny articles this is almost TF-only.
    n = len(sentences)
    df = Counter()
    for sentence_tokens in tokenized:
        df.update(set(sentence_tokens))

    scores: list[float] = []
    for sentence_tokens in tokenized:
        if not sentence_tokens:
            scores.append(0.0)
            continue
        weighted = 0.0
        for token in sentence_tokens:
            idf = math.log((1 + n) / (1 + df[token])) + 1.0
            weighted += counts[token] * idf
        scores.append(weighted / len(sentence_tokens))
    return scores


def extractive_summarize(
    text: str,
    max_sentences: int = 2,
    max_chars: int | None = 320,
    sentence_splitter=split_danish_sentences,
    strategy: str = "hybrid",
) -> str:
    """Return a short extractive summary of ``text``.

    ``strategy``:

    * ``lead`` — classic news baseline: the first ``max_sentences``.
    * ``tfidf`` — highest mean TF-IDF sentences, original order.
    * ``hybrid`` — always keep the lede, then fill with TF-IDF from the rest.

    ``max_chars`` is an optional hard cap applied after selection; if the
    joined summary still overflows, trailing sentences are dropped. When
    even the first selected sentence overflows, it is returned truncated
    on a word boundary so the toy pipeline always emits something.
    """
    if max_sentences <= 0:
        raise ValueError("max_sentences must be positive")
    if strategy not in {"lead", "tfidf", "hybrid"}:
        raise ValueError("strategy must be 'lead', 'tfidf', or 'hybrid'")

    sentences = sentence_splitter(text)
    if not sentences:
        return ""

    if len(sentences) == 1:
        return _fit_char_budget(sentences[0], max_chars)

    if strategy == "lead":
        chosen_idxs = list(range(min(max_sentences, len(sentences))))
    elif strategy == "tfidf":
        scores = sentence_scores(sentences)
        ranked = sorted(range(len(sentences)), key=lambda idx: (-scores[idx], idx))
        chosen_idxs = sorted(ranked[:max_sentences])
    else:
        chosen = {0}
        scores = sentence_scores(sentences)
        ranked = sorted(range(1, len(sentences)), key=lambda idx: (-scores[idx], idx))
        for idx in ranked:
            if len(chosen) >= max_sentences:
                break
            chosen.add(idx)
        chosen_idxs = sorted(chosen)

    chosen_sentences = [sentences[idx] for idx in chosen_idxs]
    summary = " ".join(chosen_sentences)
    return _fit_char_budget(summary, max_chars, sentences=chosen_sentences)


def _fit_char_budget(
    text: str,
    max_chars: int | None,
    sentences: list[str] | None = None,
) -> str:
    if max_chars is None or len(text) <= max_chars:
        return text

    if sentences and len(sentences) > 1:
        kept = list(sentences)
        while len(kept) > 1 and len(" ".join(kept)) > max_chars:
            kept.pop()
        joined = " ".join(kept)
        if len(joined) <= max_chars:
            return joined
        text = joined

    if len(text) <= max_chars:
        return text

    clipped = text[:max_chars].rsplit(" ", 1)[0].rstrip(" ,;:")
    return clipped or text[:max_chars]
