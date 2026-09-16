"""ROUGE-1 / ROUGE-2 / ROUGE-L without the Hugging Face metric stack.

The course scripts use ``datasets.load_metric("rouge")`` and report the
``mid.fmeasure`` fields. This module implements the same overlap
definitions on whitespace-and-punctuation tokens so the fictional
sample predictions can be scored in a clean checkout.

It is a teaching stand-in. Do not quote these numbers next to
``eval.py`` output: tokenization, stemming, and bootstrap aggregation
all differ.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from examples.danish_sentences import word_tokenize


def normalize(text: str) -> list[str]:
    """Lowercase and drop punctuation-only tokens."""
    tokens: list[str] = []
    for raw in word_tokenize(text.lower()):
        if raw.isalnum():
            tokens.append(raw)
    return tokens


def ngrams(tokens: list[str], n: int) -> Counter[tuple[str, ...]]:
    if n <= 0:
        raise ValueError("n must be positive")
    if len(tokens) < n:
        return Counter()
    return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def _fmeasure(overlap: int, pred_count: int, ref_count: int) -> tuple[float, float, float]:
    precision = overlap / pred_count if pred_count else 0.0
    recall = overlap / ref_count if ref_count else 0.0
    if precision + recall == 0:
        return precision, recall, 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def rouge_n(prediction: str, reference: str, n: int) -> tuple[float, float, float]:
    pred_grams = ngrams(normalize(prediction), n)
    ref_grams = ngrams(normalize(reference), n)
    overlap = sum((pred_grams & ref_grams).values())
    return _fmeasure(overlap, sum(pred_grams.values()), sum(ref_grams.values()))


def _lcs_length(left: list[str], right: list[str]) -> int:
    if not left or not right:
        return 0
    # Classic DP, O(len(left) * len(right)). Sample texts are short.
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


def rouge_l(prediction: str, reference: str) -> tuple[float, float, float]:
    pred_tokens = normalize(prediction)
    ref_tokens = normalize(reference)
    overlap = _lcs_length(pred_tokens, ref_tokens)
    return _fmeasure(overlap, len(pred_tokens), len(ref_tokens))


@dataclass(frozen=True)
class RougeScores:
    rouge1_precision: float
    rouge1_recall: float
    rouge1_f1: float
    rouge2_precision: float
    rouge2_recall: float
    rouge2_f1: float
    rougeL_precision: float
    rougeL_recall: float
    rougeL_f1: float

    def as_dict(self) -> dict[str, float]:
        return {
            "rouge1_precision": self.rouge1_precision,
            "rouge1_recall": self.rouge1_recall,
            "rouge1_f1": self.rouge1_f1,
            "rouge2_precision": self.rouge2_precision,
            "rouge2_recall": self.rouge2_recall,
            "rouge2_f1": self.rouge2_f1,
            "rougeL_precision": self.rougeL_precision,
            "rougeL_recall": self.rougeL_recall,
            "rougeL_f1": self.rougeL_f1,
        }


def rouge_scores(prediction: str, reference: str) -> RougeScores:
    p1, r1, f1 = rouge_n(prediction, reference, 1)
    p2, r2, f2 = rouge_n(prediction, reference, 2)
    pL, rL, fL = rouge_l(prediction, reference)
    return RougeScores(p1, r1, f1, p2, r2, f2, pL, rL, fL)


@dataclass
class CorpusRouge:
    count: int = 0
    totals: dict[str, float] = field(default_factory=dict)

    def add(self, scores: RougeScores) -> None:
        self.count += 1
        for key, value in scores.as_dict().items():
            self.totals[key] = self.totals.get(key, 0.0) + value

    def mean(self) -> dict[str, float]:
        if self.count == 0:
            return {key: 0.0 for key in RougeScores(0, 0, 0, 0, 0, 0, 0, 0, 0).as_dict()}
        return {key: value / self.count for key, value in self.totals.items()}


def rouge_corpus(
    pairs: list[tuple[str, str]],
) -> tuple[list[RougeScores], dict[str, float]]:
    """Score ``(prediction, reference)`` pairs and return per-row + mean."""
    rows: list[RougeScores] = []
    corpus = CorpusRouge()
    for prediction, reference in pairs:
        scores = rouge_scores(prediction, reference)
        rows.append(scores)
        corpus.add(scores)
    return rows, corpus.mean()
