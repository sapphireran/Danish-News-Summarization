"""Tiny ROUGE-N demonstration on the sample summaries.

This is not the Hugging Face ``rouge`` metric used in ``eval.py``. It exists
so the evaluation write-up has a runnable, dependency-free illustration:

* ROUGE-N precision = overlap / hypothesis n-grams
* ROUGE-N recall    = overlap / reference n-grams
* ROUGE-N F1        = harmonic mean

Tokenization is lowercase Unicode word characters. Danish letters are kept.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from examples.schemas import LABELED_COLUMNS, validate_csv

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"
WORD_RE = re.compile(r"[0-9A-Za-zÆØÅæøåÉéÜü]+", re.UNICODE)


def tokenize(text: str) -> List[str]:
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


def ngrams(tokens: Sequence[str], order: int) -> List[Tuple[str, ...]]:
    if order <= 0:
        raise ValueError("n-gram order must be >= 1")
    if len(tokens) < order:
        return []
    return [tuple(tokens[i : i + order]) for i in range(len(tokens) - order + 1)]


def rouge_n(prediction: str, reference: str, order: int) -> Dict[str, float]:
    pred = ngrams(tokenize(prediction), order)
    ref = ngrams(tokenize(reference), order)
    if not pred and not ref:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not pred or not ref:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    ref_counts: Dict[Tuple[str, ...], int] = {}
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
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


def _fmt(metrics: Dict[str, float]) -> str:
    return "  ".join(f"{key}={value:.3f}" for key, value in metrics.items())


def compare_pair(title: str, prediction: str, reference: str) -> None:
    print(title)
    print(f"  pred: {prediction}")
    print(f"  ref:  {reference}")
    print(f"  ROUGE-1 {_fmt(rouge_n(prediction, reference, 1))}")
    print(f"  ROUGE-2 {_fmt(rouge_n(prediction, reference, 2))}")
    print()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, default=SAMPLE_DIR)
    args = parser.parse_args(argv)

    labeled = validate_csv(args.sample_dir / "03_labeled_dataset.csv", LABELED_COLUMNS, stage="labeled")

    print("Toy ROUGE on sample silver summaries vs a slightly paraphrased hypothesis.")
    print("Official eval.py numbers use datasets.load_metric('rouge') on Nordjylland News.\n")

    paraphrases = {
        "aalborg-library-hours": (
            "Aalborg bibliotek ændrer åbningstider fra næste måned og holder "
            "længere åbent torsdag aften."
        ),
        "hjoerring-wind-meeting": (
            "Hjørring kommune inviterer til borgermøde om nye vindmøller ved kysten."
        ),
        "frederikshavn-school-wing": (
            "Skolen i Frederikshavn får en ny fløj med faglokaler næste år."
        ),
        "skagen-harbor-festival": (
            "Skagen holder havnefest i juli med musik og lokale boder."
        ),
        "viborg-museum-sunday": (
            "Viborg Museum åbner ekstra om søndagen med en udstilling om middelalderens værksteder."
        ),
    }

    for row in labeled:
        hypothesis = paraphrases.get(row["id"], row["summary"])
        compare_pair(row["id"], hypothesis, row["summary"])

    print("Identical strings should score 1.000:")
    sample = labeled[0]["summary"]
    compare_pair("identity check", sample, sample)

    print("Unrelated strings should score near 0 on ROUGE-2:")
    compare_pair(
        "unrelated check",
        "The weather in Lisbon is mild this week.",
        labeled[0]["summary"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
