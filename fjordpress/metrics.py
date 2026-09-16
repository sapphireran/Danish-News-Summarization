"""Lexical overlap metrics that do not download ``rouge-score``.

``eval.py`` used Hugging Face ``datasets.load_metric("rouge")`` plus
BERTScore with ``xlm-roberta-large``. The study kit keeps the *shape*
of those numbers — ROUGE-1/2/L mid-F — as plain Python so a laptop can
score the gazette without weights.

These are not bit-identical to the official ROUGE perl script. They are
close enough to rank two summaries of the same article.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from .tokenize import lowercase_words


@dataclass(frozen=True)
class RougeScores:
    rouge1: float
    rouge2: float
    rougeL: float
    precision1: float
    recall1: float
    precision2: float
    recall2: float
    precisionL: float
    recallL: float

    def as_dict(self, prefix: str = "") -> Dict[str, float]:
        p = f"{prefix}_" if prefix else ""
        return {
            f"{p}rouge1": self.rouge1,
            f"{p}rouge2": self.rouge2,
            f"{p}rougeL": self.rougeL,
        }


def ngrams(tokens: Sequence[str], n: int) -> List[Tuple[str, ...]]:
    if n <= 0:
        raise ValueError("n must be positive")
    if len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _f1(precision: float, recall: float) -> float:
    if precision == 0.0 and recall == 0.0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _overlap_f1(pred: Sequence[str], ref: Sequence[str], n: int) -> Tuple[float, float, float]:
    p_ng = ngrams(pred, n)
    r_ng = ngrams(ref, n)
    if not p_ng and not r_ng:
        return 1.0, 1.0, 1.0
    if not p_ng or not r_ng:
        return 0.0, 0.0, 0.0
    # Multiset overlap via counts.
    from collections import Counter

    pc = Counter(p_ng)
    rc = Counter(r_ng)
    overlap = sum((pc & rc).values())
    precision = overlap / len(p_ng)
    recall = overlap / len(r_ng)
    return precision, recall, _f1(precision, recall)


def _lcs_length(a: Sequence[str], b: Sequence[str]) -> int:
    if not a or not b:
        return 0
    # DP with two rows to keep the study kit light.
    prev = [0] * (len(b) + 1)
    for i, av in enumerate(a, start=1):
        curr = [0] * (len(b) + 1)
        for j, bv in enumerate(b, start=1):
            if av == bv:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[-1]


def _lcs_f1(pred: Sequence[str], ref: Sequence[str]) -> Tuple[float, float, float]:
    if not pred and not ref:
        return 1.0, 1.0, 1.0
    if not pred or not ref:
        return 0.0, 0.0, 0.0
    lcs = _lcs_length(pred, ref)
    precision = lcs / len(pred)
    recall = lcs / len(ref)
    return precision, recall, _f1(precision, recall)


def rouge_scores(prediction: str, reference: str) -> RougeScores:
    pred = lowercase_words(prediction)
    ref = lowercase_words(reference)
    p1, r1, f1 = _overlap_f1(pred, ref, 1)
    p2, r2, f2 = _overlap_f1(pred, ref, 2)
    pL, rL, fL = _lcs_f1(pred, ref)
    return RougeScores(
        rouge1=f1,
        rouge2=f2,
        rougeL=fL,
        precision1=p1,
        recall1=r1,
        precision2=p2,
        recall2=r2,
        precisionL=pL,
        recallL=rL,
    )


def mean_rouge(pairs: Iterable[Tuple[str, str]]) -> Dict[str, float]:
    rows = [rouge_scores(pred, ref) for pred, ref in pairs]
    if not rows:
        return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
    n = len(rows)
    return {
        "rouge1": sum(r.rouge1 for r in rows) / n,
        "rouge2": sum(r.rouge2 for r in rows) / n,
        "rougeL": sum(r.rougeL for r in rows) / n,
    }


def compression_ratio(source: str, summary: str) -> float:
    """Summary words / source words. 0 if the source is empty."""
    src_n = len(lowercase_words(source))
    if src_n == 0:
        return 0.0
    return len(lowercase_words(summary)) / src_n


def token_jaccard(a: str, b: str) -> float:
    sa = set(lowercase_words(a))
    sb = set(lowercase_words(b))
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
