#!/usr/bin/env python3
"""Toy overlap metrics on hand-written Danish prediction/reference pairs.

This is *not* ROUGE from Google's ``rouge-score`` package and *not* BERTScore.
It exists to make two points without a GPU:

1. Unigram F1 and LCS ratio move like ROUGE-1 / ROUGE-L on clean matches.
2. A fluent fact-swap can still score well — overlap is not factuality.

Pairs are original documentation text, not model output from the 2023 run.

Usage (from repo root):

    python examples/metrics_toy_eval.py
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class Pair:
    name: str
    reference: str
    prediction: str
    note: str


PAIRS: List[Pair] = [
    Pair(
        name="exact_match",
        reference="Havneby åbner en ny cykelsti mellem stationen og havnen.",
        prediction="Havneby åbner en ny cykelsti mellem stationen og havnen.",
        note="Upper bound: both token F1 and LCS ratio should be 1.0.",
    ),
    Pair(
        name="close_paraphrase",
        reference="Havneby åbner en ny cykelsti mellem stationen og havnen.",
        prediction="I Havneby åbner kommunen en cykelsti fra stationen til havnen.",
        note="Most content words overlap; function words differ.",
    ),
    Pair(
        name="fact_swap_budget",
        reference=(
            "Kommunen bruger 12 millioner kroner på cykelstien i Havneby."
        ),
        prediction=(
            "Kommunen bruger 21 millioner kroner på cykelstien i Havneby."
        ),
        note=(
            "12 vs 21 is a serious factual error. Overlap metrics barely move "
            "because only one token changed."
        ),
    ),
    Pair(
        name="entity_swap",
        reference="Borgmesteren i Havneby kalder stien et løft for pendlere.",
        prediction="Borgmesteren i Skovby kalder stien et løft for pendlere.",
        note="Wrong town. Unigram F1 stays high; a reader would reject it.",
    ),
    Pair(
        name="unrelated_fluent",
        reference="Havneby åbner en ny cykelsti mellem stationen og havnen.",
        prediction="Fodboldklubben vandt 3-1 og rykker op i næste række.",
        note="Fluent Danish, zero topical overlap. Scores should collapse.",
    ),
]


def tokenize(text: str) -> List[str]:
    """Lowercase whitespace tokens, stripping a small Danish punctuation set."""
    out = []
    for raw in text.lower().split():
        token = raw.strip(".,;:!?\"'«»()[]")
        if token:
            out.append(token)
    return out


def token_f1(reference: Sequence[str], prediction: Sequence[str]) -> float:
    """Multiset unigram F1 (ROUGE-1-shaped)."""
    if not reference and not prediction:
        return 1.0
    if not reference or not prediction:
        return 0.0
    ref_counts: dict[str, int] = {}
    pred_counts: dict[str, int] = {}
    for tok in reference:
        ref_counts[tok] = ref_counts.get(tok, 0) + 1
    for tok in prediction:
        pred_counts[tok] = pred_counts.get(tok, 0) + 1
    overlap = 0
    for tok, count in pred_counts.items():
        overlap += min(count, ref_counts.get(tok, 0))
    precision = overlap / sum(pred_counts.values())
    recall = overlap / sum(ref_counts.values())
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def lcs_length(a: Sequence[str], b: Sequence[str]) -> int:
    """Standard DP longest common subsequence length."""
    n, m = len(a), len(b)
    dp = [0] * (m + 1)
    for i in range(1, n + 1):
        prev = 0
        for j in range(1, m + 1):
            temp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = temp
    return dp[m]


def lcs_ratio(reference: Sequence[str], prediction: Sequence[str]) -> float:
    """LCS / max(len). 1.0 on exact match; 0.0 on disjoint sequences."""
    if not reference and not prediction:
        return 1.0
    denom = max(len(reference), len(prediction))
    if denom == 0:
        return 0.0
    return lcs_length(reference, prediction) / denom


@dataclass(frozen=True)
class ScoredPair:
    name: str
    token_f1: float
    lcs_ratio: float
    note: str
    reference: str
    prediction: str


def score_pair(pair: Pair) -> ScoredPair:
    ref = tokenize(pair.reference)
    pred = tokenize(pair.prediction)
    return ScoredPair(
        name=pair.name,
        token_f1=round(token_f1(ref, pred), 4),
        lcs_ratio=round(lcs_ratio(ref, pred), 4),
        note=pair.note,
        reference=pair.reference,
        prediction=pair.prediction,
    )


def score_all(pairs: Iterable[Pair] | None = None) -> List[ScoredPair]:
    return [score_pair(p) for p in (pairs or PAIRS)]


def render(rows: Sequence[ScoredPair]) -> str:
    lines = [
        "Toy overlap metrics (whitespace unigrams, not official ROUGE)",
        "",
        f"{'name':22s}  {'F1':>6s}  {'LCS':>6s}  lesson",
        "-" * 88,
    ]
    for row in rows:
        lines.append(
            f"{row.name:22s}  {row.token_f1:6.3f}  {row.lcs_ratio:6.3f}  {row.note}"
        )
    lines.append("")
    lines.append(
        "Read the fact_swap_budget and entity_swap rows before trusting a ROUGE table."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Dump scored pairs as JSON instead of a table",
    )
    args = parser.parse_args(argv)
    rows = score_all()
    if args.json:
        json.dump([asdict(r) for r in rows], sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(render(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
