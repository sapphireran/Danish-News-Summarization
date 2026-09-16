"""Reference metrics used to talk about silver-label quality.

`eval.py` reports Hugging Face `rouge` and `bertscore` against Nordjylland
gold summaries. Those metrics need checkpoints and the `evaluate` / `rouge`
packages. The implementations here are small enough to run in the examples
folder with no extra dependencies, and they match the usual definitions:

* ROUGE-N is overlap of n-grams (precision, recall, F1).
* ROUGE-L is the F1 of the longest common subsequence.
* Compression ratio is `summary_tokens / article_tokens`.
* Novelty is the share of summary n-grams that never appear in the article.

These numbers are for documentation and regression tests, not a replacement
for the course evaluation script.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

_TOKEN = re.compile(r"[A-Za-zÆØÅæøå0-9]+(?:'[A-Za-zÆØÅæøå0-9]+)?", re.UNICODE)


@dataclass(frozen=True)
class OverlapScores:
    precision: float
    recall: float
    f1: float

    def as_dict(self, prefix: str) -> dict[str, float]:
        return {
            f"{prefix}_precision": self.precision,
            f"{prefix}_recall": self.recall,
            f"{prefix}_f1": self.f1,
        }


@dataclass(frozen=True)
class PairReport:
    rouge1: OverlapScores
    rouge2: OverlapScores
    rougeL: OverlapScores
    compression: float
    novelty_unigram: float
    pred_tokens: int
    ref_tokens: int
    src_tokens: int

    def as_dict(self) -> dict[str, float | int]:
        payload: dict[str, float | int] = {
            "compression": self.compression,
            "novelty_unigram": self.novelty_unigram,
            "pred_tokens": self.pred_tokens,
            "ref_tokens": self.ref_tokens,
            "src_tokens": self.src_tokens,
        }
        payload.update(self.rouge1.as_dict("rouge1"))
        payload.update(self.rouge2.as_dict("rouge2"))
        payload.update(self.rougeL.as_dict("rougeL"))
        return payload


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokens, keeping Danish vowels."""
    return [match.group(0).lower() for match in _TOKEN.finditer(text or "")]


def ngrams(tokens: Sequence[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0:
        raise ValueError("n must be positive")
    if len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _f1(precision: float, recall: float) -> float:
    if precision == 0.0 and recall == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def _overlap(pred: Sequence[tuple[str, ...]], ref: Sequence[tuple[str, ...]]) -> OverlapScores:
    if not pred and not ref:
        return OverlapScores(1.0, 1.0, 1.0)
    if not pred or not ref:
        return OverlapScores(0.0, 0.0, 0.0)
    ref_counts: dict[tuple[str, ...], int] = {}
    for gram in ref:
        ref_counts[gram] = ref_counts.get(gram, 0) + 1
    overlap = 0
    for gram in pred:
        remaining = ref_counts.get(gram, 0)
        if remaining:
            overlap += 1
            ref_counts[gram] = remaining - 1
    precision = overlap / len(pred)
    recall = overlap / len(ref)
    return OverlapScores(precision, recall, _f1(precision, recall))


def rouge_n(prediction: str, reference: str, n: int = 1) -> OverlapScores:
    """ROUGE-N with clipped counts (each reference n-gram used at most once)."""
    return _overlap(ngrams(tokenize(prediction), n), ngrams(tokenize(reference), n))


def _lcs_length(left: Sequence[str], right: Sequence[str]) -> int:
    if not left or not right:
        return 0
    # Hunt–Szymanski style DP over the shorter axis.
    if len(right) < len(left):
        left, right = right, left
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


def rouge_l(prediction: str, reference: str) -> OverlapScores:
    """ROUGE-L using LCS(pred, ref) / |pred| and LCS / |ref|."""
    pred_tokens = tokenize(prediction)
    ref_tokens = tokenize(reference)
    if not pred_tokens and not ref_tokens:
        return OverlapScores(1.0, 1.0, 1.0)
    if not pred_tokens or not ref_tokens:
        return OverlapScores(0.0, 0.0, 0.0)
    lcs = _lcs_length(pred_tokens, ref_tokens)
    precision = lcs / len(pred_tokens)
    recall = lcs / len(ref_tokens)
    return OverlapScores(precision, recall, _f1(precision, recall))


def compression_ratio(summary: str, source: str) -> float:
    """`|summary| / |source|` in tokens. Empty source → `math.inf` if summary exists."""
    src = tokenize(source)
    pred = tokenize(summary)
    if not src:
        return math.inf if pred else 0.0
    return len(pred) / len(src)


def novelty_rate(summary: str, source: str, n: int = 1) -> float:
    """Share of summary n-grams that never occur in the source."""
    pred = ngrams(tokenize(summary), n)
    if not pred:
        return 0.0
    src = set(ngrams(tokenize(source), n))
    novel = sum(1 for gram in pred if gram not in src)
    return novel / len(pred)


def score_pair(prediction: str, reference: str, source: str | None = None) -> PairReport:
    """Score one summary against a reference, optionally also against its article."""
    src = source if source is not None else reference
    return PairReport(
        rouge1=rouge_n(prediction, reference, 1),
        rouge2=rouge_n(prediction, reference, 2),
        rougeL=rouge_l(prediction, reference),
        compression=compression_ratio(prediction, src),
        novelty_unigram=novelty_rate(prediction, src, 1),
        pred_tokens=len(tokenize(prediction)),
        ref_tokens=len(tokenize(reference)),
        src_tokens=len(tokenize(src)),
    )


def mean_reports(reports: Iterable[PairReport]) -> dict[str, float]:
    """Micro-average the numeric fields of several `PairReport`s."""
    rows = [asdict(report) for report in reports]
    if not rows:
        return {}
    flat: dict[str, list[float]] = {}
    for row in rows:
        for key, value in _flatten(row).items():
            flat.setdefault(key, []).append(float(value))
    return {key: sum(values) / len(values) for key, values in flat.items()}


def _flatten(row: dict[str, object], prefix: str = "") -> dict[str, float]:
    out: dict[str, float] = {}
    for key, value in row.items():
        name = f"{prefix}{key}" if not prefix else f"{prefix}_{key}"
        if isinstance(value, dict):
            out.update(_flatten(value, name))
        else:
            out[name] = float(value)  # type: ignore[arg-type]
    return out
