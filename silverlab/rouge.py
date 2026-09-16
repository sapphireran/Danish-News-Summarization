"""Pedagogical ROUGE-N and ROUGE-L. No `evaluate` or `datasets` dependency.

The 2023 trainer called `datasets.load_metric("rouge")` and kept the mid
F-measure. This module exposes the same three numbers (precision, recall, F)
so the lab can talk about overlap without inventing a 2023 scoreboard.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

from .tokenize import ngrams, tokenize


@dataclass(frozen=True)
class Score:
    precision: float
    recall: float
    fmeasure: float

    def as_dict(self, prefix: str) -> dict[str, float]:
        return {
            f"{prefix}_precision": self.precision,
            f"{prefix}_recall": self.recall,
            f"{prefix}_fmeasure": self.fmeasure,
        }


def _safe_f(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def _empty() -> Score:
    return Score(0.0, 0.0, 0.0)


def rouge_n(prediction: str, reference: str, n: int = 1) -> Score:
    """ROUGE-N with clipped n-gram counts (Lin 2004)."""
    if n < 1:
        raise ValueError("n must be >= 1")
    pred_grams = ngrams(tokenize(prediction), n)
    ref_grams = ngrams(tokenize(reference), n)
    if not pred_grams or not ref_grams:
        return _empty()
    overlap = sum((Counter(pred_grams) & Counter(ref_grams)).values())
    precision = overlap / len(pred_grams)
    recall = overlap / len(ref_grams)
    return Score(precision, recall, _safe_f(precision, recall))


def lcs_length(left: Sequence[str], right: Sequence[str]) -> int:
    """Length of the longest common subsequence. O(len(left) * len(right))."""
    if not left or not right:
        return 0
    # Previous/current rows only — the lab articles are short.
    previous = [0] * (len(right) + 1)
    for token in left:
        current = [0]
        for j, other in enumerate(right, start=1):
            if token == other:
                current.append(previous[j - 1] + 1)
            else:
                current.append(max(previous[j], current[-1]))
        previous = current
    return previous[-1]


def rouge_l(prediction: str, reference: str) -> Score:
    """Sentence-level ROUGE-L (LCS F-measure) without the summary-level union."""
    pred_tokens = tokenize(prediction)
    ref_tokens = tokenize(reference)
    if not pred_tokens or not ref_tokens:
        return _empty()
    overlap = lcs_length(pred_tokens, ref_tokens)
    precision = overlap / len(pred_tokens)
    recall = overlap / len(ref_tokens)
    return Score(precision, recall, _safe_f(precision, recall))


def score_pair(prediction: str, reference: str) -> dict[str, float]:
    """Bundle ROUGE-1/2/L F-measures plus precision/recall for tables."""
    r1 = rouge_n(prediction, reference, 1)
    r2 = rouge_n(prediction, reference, 2)
    rl = rouge_l(prediction, reference)
    out: dict[str, float] = {}
    out.update(r1.as_dict("rouge1"))
    out.update(r2.as_dict("rouge2"))
    out.update(rl.as_dict("rougeL"))
    return out


def mean_scores(rows: Iterable[dict[str, float]]) -> dict[str, float]:
    material = list(rows)
    if not material:
        return {}
    keys = material[0].keys()
    return {key: sum(row[key] for row in material) / len(material) for key in keys}
