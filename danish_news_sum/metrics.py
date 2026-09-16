"""Offline lexical metrics for the example evaluation walkthrough.

The original ``eval.py`` reports Hugging Face ROUGE and Danish BERTScore.
Those require model downloads. This module implements the same *shapes*
(unigram / bigram overlap and LCS F1) so ``examples/score_sample_summaries.py``
can show the numbers on the committed fixtures without a GPU.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Sequence

_TOKEN = re.compile(r"\w+", flags=re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN.findall(text or "")]


def ngrams(tokens: Sequence[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0:
        raise ValueError("n must be a positive integer")
    if len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _f1(precision: float, recall: float) -> float:
    if precision == 0.0 and recall == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def ngram_f1(prediction: str, reference: str, n: int = 1) -> dict[str, float]:
    """ROUGE-N style overlap on whitespace/word tokens."""
    pred_grams = ngrams(tokenize(prediction), n)
    ref_grams = ngrams(tokenize(reference), n)
    if not pred_grams and not ref_grams:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not pred_grams or not ref_grams:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    ref_counts: dict[tuple[str, ...], int] = {}
    for gram in ref_grams:
        ref_counts[gram] = ref_counts.get(gram, 0) + 1

    overlap = 0
    for gram in pred_grams:
        remaining = ref_counts.get(gram, 0)
        if remaining > 0:
            overlap += 1
            ref_counts[gram] = remaining - 1

    precision = overlap / len(pred_grams)
    recall = overlap / len(ref_grams)
    return {"precision": precision, "recall": recall, "f1": _f1(precision, recall)}


def token_overlap(prediction: str, reference: str) -> dict[str, float]:
    return ngram_f1(prediction, reference, n=1)


def _lcs_length(left: Sequence[str], right: Sequence[str]) -> int:
    if not left or not right:
        return 0
    previous = [0] * (len(right) + 1)
    for left_token in left:
        current = [0]
        for j, right_token in enumerate(right, start=1):
            if left_token == right_token:
                current.append(previous[j - 1] + 1)
            else:
                current.append(max(previous[j], current[-1]))
        previous = current
    return previous[-1]


def lcs_f1(prediction: str, reference: str) -> dict[str, float]:
    """ROUGE-L style F1 from the longest common subsequence of tokens."""
    pred_tokens = tokenize(prediction)
    ref_tokens = tokenize(reference)
    if not pred_tokens and not ref_tokens:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not pred_tokens or not ref_tokens:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    lcs = _lcs_length(pred_tokens, ref_tokens)
    precision = lcs / len(pred_tokens)
    recall = lcs / len(ref_tokens)
    return {"precision": precision, "recall": recall, "f1": _f1(precision, recall)}


def compression_ratio(article: str, summary: str) -> float:
    article_tokens = len(tokenize(article))
    summary_tokens = len(tokenize(summary))
    if summary_tokens == 0:
        return math.inf
    return article_tokens / summary_tokens


def mean(values: Iterable[float]) -> float:
    materialised = list(values)
    if not materialised:
        return 0.0
    return sum(materialised) / len(materialised)


def lexical_scores(prediction: str, reference: str, article: str | None = None) -> dict[str, float]:
    """Bundle the example-script metrics for one prediction / reference pair."""
    rouge1 = ngram_f1(prediction, reference, n=1)
    rouge2 = ngram_f1(prediction, reference, n=2)
    rouge_l = lcs_f1(prediction, reference)
    scores = {
        "rouge1_precision": rouge1["precision"],
        "rouge1_recall": rouge1["recall"],
        "rouge1_f1": rouge1["f1"],
        "rouge2_precision": rouge2["precision"],
        "rouge2_recall": rouge2["recall"],
        "rouge2_f1": rouge2["f1"],
        "rougeL_precision": rouge_l["precision"],
        "rougeL_recall": rouge_l["recall"],
        "rougeL_f1": rouge_l["f1"],
        "pred_tokens": float(len(tokenize(prediction))),
        "ref_tokens": float(len(tokenize(reference))),
    }
    if article is not None:
        scores["compression_ratio"] = compression_ratio(article, prediction)
    return scores


def aggregate_scores(rows: Sequence[dict[str, float]]) -> dict[str, float]:
    if not rows:
        return {}
    keys = rows[0].keys()
    return {key: mean(row[key] for row in rows) for key in keys}
