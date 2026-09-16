"""Extractive Danish baselines that need no weights.

The 2023 project jumped straight to a cross-lingual abstractive teacher. A
personal lab should be able to say whether lead-2 already covers the gold
extractive sentence before anyone converts OPUS-MT to CTranslate2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from .sentences import split_sentences
from .tokenize import content_tokens, tokenize

BASELINE_NAMES = ("lead1", "lead2", "longest", "keyword", "textrank")


@dataclass(frozen=True)
class BaselineResult:
    name: str
    summary: str
    sentence_indices: tuple[int, ...]


def _join_in_order(sentences: Sequence[str], indices: Iterable[int]) -> str:
    ordered = sorted(set(indices))
    return " ".join(sentences[i] for i in ordered if 0 <= i < len(sentences))


def summarize_lead(text: str, k: int = 1) -> BaselineResult:
    sentences = split_sentences(text)
    if not sentences:
        return BaselineResult(f"lead{k}", "", ())
    take = min(k, len(sentences))
    indices = tuple(range(take))
    name = f"lead{k}"
    return BaselineResult(name, _join_in_order(sentences, indices), indices)


def summarize_longest(text: str, k: int = 1) -> BaselineResult:
    sentences = split_sentences(text)
    if not sentences:
        return BaselineResult("longest", "", ())
    ranked = sorted(
        range(len(sentences)),
        key=lambda i: (-len(tokenize(sentences[i])), i),
    )
    indices = tuple(ranked[: min(k, len(sentences))])
    return BaselineResult("longest", _join_in_order(sentences, indices), indices)


def summarize_keyword(text: str, title: str, k: int = 2) -> BaselineResult:
    """Rank sentences by overlap with the title's content words."""
    sentences = split_sentences(text)
    if not sentences:
        return BaselineResult("keyword", "", ())
    keys = set(content_tokens(title))
    if not keys:
        fallback = summarize_lead(text, k=1)
        return BaselineResult("keyword", fallback.summary, fallback.sentence_indices)

    def score(index: int) -> tuple[int, int]:
        overlap = len(set(content_tokens(sentences[index])) & keys)
        return (-overlap, index)

    ranked = sorted(range(len(sentences)), key=score)
    indices = tuple(ranked[: min(k, len(sentences))])
    return BaselineResult("keyword", _join_in_order(sentences, indices), indices)


def _similarity(left: str, right: str) -> float:
    a = set(content_tokens(left))
    b = set(content_tokens(right))
    if not a or not b:
        return 0.0
    return len(a & b) / (math.log(len(a) + 1.0) + math.log(len(b) + 1.0))


def textrank_scores(
    sentences: Sequence[str],
    damping: float = 0.85,
    iterations: int = 40,
) -> list[float]:
    """PageRank on a fully connected sentence graph (Mihalcea & Tarau 2004)."""
    count = len(sentences)
    if count == 0:
        return []
    if count == 1:
        return [1.0]
    weights = [
        [
            0.0 if i == j else _similarity(sentences[i], sentences[j])
            for j in range(count)
        ]
        for i in range(count)
    ]
    out_degree = [sum(row) or 1.0 for row in weights]
    scores = [1.0 / count] * count
    teleport = (1.0 - damping) / count
    for _ in range(iterations):
        nxt = []
        for i in range(count):
            inbound = 0.0
            for j in range(count):
                inbound += weights[j][i] / out_degree[j] * scores[j]
            nxt.append(teleport + damping * inbound)
        scores = nxt
    return scores


def summarize_textrank(text: str, k: int = 2) -> BaselineResult:
    sentences = split_sentences(text)
    if not sentences:
        return BaselineResult("textrank", "", ())
    scores = textrank_scores(sentences)
    ranked = sorted(range(len(sentences)), key=lambda i: (-scores[i], i))
    indices = tuple(ranked[: min(k, len(sentences))])
    return BaselineResult("textrank", _join_in_order(sentences, indices), indices)


def run_all_baselines(text: str, title: str = "") -> dict[str, BaselineResult]:
    """Named bundle used by the CLI and the HTML report."""
    return {
        "lead1": summarize_lead(text, k=1),
        "lead2": summarize_lead(text, k=2),
        "longest": summarize_longest(text, k=1),
        "keyword": summarize_keyword(text, title, k=2),
        "textrank": summarize_textrank(text, k=2),
    }


BASELINE_FUNCS: dict[str, Callable[..., BaselineResult]] = {
    "lead1": lambda text, title="": summarize_lead(text, k=1),
    "lead2": lambda text, title="": summarize_lead(text, k=2),
    "longest": lambda text, title="": summarize_longest(text, k=1),
    "keyword": lambda text, title="": summarize_keyword(text, title, k=2),
    "textrank": lambda text, title="": summarize_textrank(text, k=2),
}
