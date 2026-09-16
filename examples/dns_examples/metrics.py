"""Tiny overlap metrics for the toy hop-comparison script.

These are not the Hugging Face `rouge` / `bertscore` objects used in
`eval.py`. They are unigram/bigram/LCS F-measures on Unicode word tokens
so a laptop without `evaluate` can still show that silver labels are
*shorter* than articles and only partly overlap them.

Do not quote these numbers as 2023 results. The 2023 run left no scores
in git.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_WORD = re.compile(r"\w+", re.UNICODE)


def word_tokens(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0:
        raise ValueError("n must be >= 1")
    if len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _fmeasure(precision: float, recall: float) -> float:
    if precision == 0.0 and recall == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def _overlap_f(pred: list[tuple[str, ...]], ref: list[tuple[str, ...]]) -> tuple[float, float, float]:
    if not pred and not ref:
        return 1.0, 1.0, 1.0
    if not pred or not ref:
        return 0.0, 0.0, 0.0
    ref_counts: dict[tuple[str, ...], int] = {}
    for gram in ref:
        ref_counts[gram] = ref_counts.get(gram, 0) + 1
    overlap = 0
    for gram in pred:
        leftover = ref_counts.get(gram, 0)
        if leftover:
            overlap += 1
            ref_counts[gram] = leftover - 1
    precision = overlap / len(pred)
    recall = overlap / len(ref)
    return precision, recall, _fmeasure(precision, recall)


def rouge_n(prediction: str, reference: str, n: int = 1) -> tuple[float, float, float]:
    """Return (precision, recall, f1) for ROUGE-N on word tokens."""
    return _overlap_f(ngrams(word_tokens(prediction), n), ngrams(word_tokens(reference), n))


def lcs_length(left: list[str], right: list[str]) -> int:
    """Length of the longest common subsequence (not substring)."""
    if not left or not right:
        return 0
    # Classic DP, O(len(left) * len(right)). Fine for news sentences.
    prev = [0] * (len(right) + 1)
    for token in left:
        current = [0]
        for j, other in enumerate(right, start=1):
            if token == other:
                current.append(prev[j - 1] + 1)
            else:
                current.append(max(prev[j], current[-1]))
        prev = current
    return prev[-1]


def rouge_l(prediction: str, reference: str) -> tuple[float, float, float]:
    pred = word_tokens(prediction)
    ref = word_tokens(reference)
    if not pred and not ref:
        return 1.0, 1.0, 1.0
    if not pred or not ref:
        return 0.0, 0.0, 0.0
    overlap = lcs_length(pred, ref)
    precision = overlap / len(pred)
    recall = overlap / len(ref)
    return precision, recall, _fmeasure(precision, recall)


def compression_ratio(article: str, summary: str) -> float:
    """summary tokens / article tokens. 0 if the article is empty."""
    article_n = len(word_tokens(article))
    if article_n == 0:
        return 0.0
    return len(word_tokens(summary)) / article_n


@dataclass(frozen=True)
class PairScores:
    id: str
    rouge1_f: float
    rouge2_f: float
    rougeL_f: float
    compression: float
    article_tokens: int
    summary_tokens: int


def summarize_pair(row_id: str, article: str, summary: str) -> PairScores:
    return PairScores(
        id=row_id,
        rouge1_f=rouge_n(summary, article, 1)[2],
        rouge2_f=rouge_n(summary, article, 2)[2],
        rougeL_f=rouge_l(summary, article)[2],
        compression=compression_ratio(article, summary),
        article_tokens=len(word_tokens(article)),
        summary_tokens=len(word_tokens(summary)),
    )
