#!/usr/bin/env python3
"""Stdlib stand-ins for the ROUGE-style numbers used in training.

``finetune.py`` and ``eval.py`` call Hugging Face ``rouge`` (and BERTScore
in eval). Those libraries need model downloads. This script scores the
fiction corpus against ``toy_predictions.csv`` with:

* unigram precision / recall / F1  (a ROUGE-1 sketch)
* LCS F1                           (a ROUGE-L sketch)
* character compression ratio      (len(summary) / len(body))

It is documentation, not a substitute for ``eval.py``.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

from schema import STAGE_FILES, columns_for, validate_headers  # noqa: E402

DATA_DIR = EXAMPLES_DIR / "data"
_TOKEN_SPLIT = __import__("re").compile(r"[^\wæøåÆØÅ]+", flags=__import__("re").UNICODE)


@dataclass(frozen=True)
class RowScore:
    id: str
    unigram_precision: float
    unigram_recall: float
    unigram_f1: float
    lcs_f1: float
    compression: float


def tokenize(text: str) -> list[str]:
    return [tok.lower() for tok in _TOKEN_SPLIT.split(text) if tok]


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def unigram_scores(pred: str, ref: str) -> tuple[float, float, float]:
    pred_tokens = tokenize(pred)
    ref_tokens = tokenize(ref)
    if not pred_tokens and not ref_tokens:
        return 1.0, 1.0, 1.0
    if not pred_tokens or not ref_tokens:
        return 0.0, 0.0, 0.0
    pred_counts: dict[str, int] = {}
    ref_counts: dict[str, int] = {}
    for tok in pred_tokens:
        pred_counts[tok] = pred_counts.get(tok, 0) + 1
    for tok in ref_tokens:
        ref_counts[tok] = ref_counts.get(tok, 0) + 1
    overlap = 0
    for tok, count in pred_counts.items():
        overlap += min(count, ref_counts.get(tok, 0))
    precision = overlap / len(pred_tokens)
    recall = overlap / len(ref_tokens)
    return precision, recall, _f1(precision, recall)


def lcs_length(pred_tokens: list[str], ref_tokens: list[str]) -> int:
    if not pred_tokens or not ref_tokens:
        return 0
    # Classic DP, fine for short example summaries.
    n, m = len(pred_tokens), len(ref_tokens)
    prev = [0] * (m + 1)
    for i in range(1, n + 1):
        curr = [0] * (m + 1)
        for j in range(1, m + 1):
            if pred_tokens[i - 1] == ref_tokens[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[m]


def lcs_f1(pred: str, ref: str) -> float:
    pred_tokens = tokenize(pred)
    ref_tokens = tokenize(ref)
    if not pred_tokens and not ref_tokens:
        return 1.0
    if not pred_tokens or not ref_tokens:
        return 0.0
    overlap = lcs_length(pred_tokens, ref_tokens)
    precision = overlap / len(pred_tokens)
    recall = overlap / len(ref_tokens)
    return _f1(precision, recall)


def compression_ratio(summary: str, body: str) -> float:
    if not body:
        return 0.0
    return len(summary) / len(body)


def load_labeled(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        validate_headers("labeled", reader.fieldnames or [])
        return {row["id"]: row for row in reader}


def load_predictions(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        validate_headers("predictions", reader.fieldnames or [])
        return {row["id"]: row["summary"] for row in reader}


def score_corpus(
    labeled_path: Path,
    pred_path: Path,
) -> list[RowScore]:
    labeled = load_labeled(labeled_path)
    preds = load_predictions(pred_path)
    if set(labeled) != set(preds):
        missing = set(labeled) ^ set(preds)
        raise ValueError(f"id mismatch between labeled and predictions: {sorted(missing)}")
    rows: list[RowScore] = []
    for article_id in sorted(labeled):
        gold = labeled[article_id]["summary"]
        pred = preds[article_id]
        precision, recall, f1 = unigram_scores(pred, gold)
        rows.append(
            RowScore(
                id=article_id,
                unigram_precision=precision,
                unigram_recall=recall,
                unigram_f1=f1,
                lcs_f1=lcs_f1(pred, gold),
                compression=compression_ratio(pred, labeled[article_id]["body"]),
            )
        )
    return rows


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def format_table(rows: list[RowScore]) -> str:
    header = (
        f"{'id':<8} {'P':>6} {'R':>6} {'F1':>6} {'LCS':>6} {'comp':>6}"
    )
    lines = [header, "-" * len(header)]
    for row in rows:
        lines.append(
            f"{row.id:<8} {row.unigram_precision:6.3f} {row.unigram_recall:6.3f} "
            f"{row.unigram_f1:6.3f} {row.lcs_f1:6.3f} {row.compression:6.3f}"
        )
    lines.append("-" * len(header))
    lines.append(
        f"{'macro':<8} {mean([r.unigram_precision for r in rows]):6.3f} "
        f"{mean([r.unigram_recall for r in rows]):6.3f} "
        f"{mean([r.unigram_f1 for r in rows]):6.3f} "
        f"{mean([r.lcs_f1 for r in rows]):6.3f} "
        f"{mean([r.compression for r in rows]):6.3f}"
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--labeled",
        type=Path,
        default=DATA_DIR / STAGE_FILES["labeled"],
    )
    parser.add_argument(
        "--predictions",
        type=Path,
        default=DATA_DIR / STAGE_FILES["predictions"],
    )
    args = parser.parse_args()
    rows = score_corpus(args.labeled, args.predictions)
    print("Toy unigram / LCS scores (not Hugging Face ROUGE)")
    print("P/R/F1 = unigram overlap vs gold Danish summary")
    print("LCS    = longest common subsequence F1")
    print("comp   = len(prediction) / len(Danish body)")
    print()
    print(format_table(rows))
    print()
    print("Reading notes are in examples/corpus.py (SampleArticle.notes).")
    # Silence unused import warning in some linters; documents the contract.
    assert columns_for("predictions") == ("id", "summary")


if __name__ == "__main__":
    main()
