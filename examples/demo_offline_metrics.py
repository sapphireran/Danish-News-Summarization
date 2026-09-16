#!/usr/bin/env python3
"""Toy lexical overlap metrics on the synthetic public-eval set.

This is **not** the Hugging Face ``rouge`` metric and not BERTScore.
It exists so the eval schema can be exercised without downloading
``xlm-roberta-large``.

For each row we score:

1. A naive baseline: the first sentence of ``input_text`` as if it were a summary.
2. The gold ``target_text`` against itself (sanity upper bound ≈ 1.0).

    python examples/demo_offline_metrics.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csv_io import DATA_DIR, read_jsonl  # noqa: E402
from text_chunking import simple_sent_tokenize  # noqa: E402


def normalize(text: str) -> List[str]:
    folded = (
        text.lower()
        .replace("æ", "ae")
        .replace("ø", "oe")
        .replace("å", "aa")
    )
    out: List[str] = []
    buf: List[str] = []
    for ch in folded:
        if ch.isalnum():
            buf.append(ch)
        else:
            if buf:
                out.append("".join(buf))
                buf.clear()
    if buf:
        out.append("".join(buf))
    return out


def ngrams(tokens: Sequence[str], n: int) -> List[Tuple[str, ...]]:
    if len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def overlap_f1(pred: Sequence[str], ref: Sequence[str], n: int) -> float:
    pred_n = ngrams(pred, n)
    ref_n = ngrams(ref, n)
    if not pred_n and not ref_n:
        return 1.0
    if not pred_n or not ref_n:
        return 0.0
    ref_bag = list(ref_n)
    hits = 0
    for gram in pred_n:
        if gram in ref_bag:
            hits += 1
            ref_bag.remove(gram)
    precision = hits / len(pred_n)
    recall = hits / len(ref_n)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def lcs_length(a: Sequence[str], b: Sequence[str]) -> int:
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for tok_a in a:
        cur = [0]
        for j, tok_b in enumerate(b, start=1):
            if tok_a == tok_b:
                cur.append(prev[j - 1] + 1)
            else:
                cur.append(max(prev[j], cur[-1]))
        prev = cur
    return prev[-1]


def lcs_f1(pred: Sequence[str], ref: Sequence[str]) -> float:
    if not pred and not ref:
        return 1.0
    if not pred or not ref:
        return 0.0
    lcs = lcs_length(pred, ref)
    precision = lcs / len(pred)
    recall = lcs / len(ref)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def score_pair(pred_text: str, ref_text: str) -> dict:
    pred = normalize(pred_text)
    ref = normalize(ref_text)
    return {
        "unigram_f1": round(overlap_f1(pred, ref, 1), 4),
        "bigram_f1": round(overlap_f1(pred, ref, 2), 4),
        "lcs_f1": round(lcs_f1(pred, ref), 4),
        "pred_tokens": len(pred),
        "ref_tokens": len(ref),
    }


def mean_metric(rows: Iterable[dict], key: str) -> float:
    values = [row[key] for row in rows]
    return round(sum(values) / len(values), 4) if values else 0.0


def first_sentence(text: str) -> str:
    sentences = simple_sent_tokenize(text)
    return sentences[0] if sentences else text


def main() -> int:
    path = DATA_DIR / "sample_public_eval.jsonl"
    gold_rows = read_jsonl(path)
    if len(gold_rows) < 3:
        raise SystemExit("public eval fixture is too small")

    baseline_rows = []
    identity_rows = []
    for row in gold_rows:
        pred = first_sentence(row["input_text"])
        ref = row["target_text"]
        base = score_pair(pred, ref)
        ident = score_pair(ref, ref)
        base["id"] = row["id"]
        ident["id"] = row["id"]
        baseline_rows.append(base)
        identity_rows.append(ident)
        if ident["unigram_f1"] != 1.0:
            raise SystemExit(f"{row['id']}: identity unigram F1 is not 1.0")

    summary = {
        "note": "Toy overlap, not Hugging Face ROUGE / BERTScore.",
        "n": len(gold_rows),
        "baseline_first_sentence": {
            "unigram_f1": mean_metric(baseline_rows, "unigram_f1"),
            "bigram_f1": mean_metric(baseline_rows, "bigram_f1"),
            "lcs_f1": mean_metric(baseline_rows, "lcs_f1"),
        },
        "identity_upper_bound": {
            "unigram_f1": mean_metric(identity_rows, "unigram_f1"),
            "bigram_f1": mean_metric(identity_rows, "bigram_f1"),
            "lcs_f1": mean_metric(identity_rows, "lcs_f1"),
        },
        "per_row_baseline": baseline_rows,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    base_u = summary["baseline_first_sentence"]["unigram_f1"]
    ident_u = summary["identity_upper_bound"]["unigram_f1"]
    if not ident_u == 1.0:
        raise SystemExit("identity baseline drifted")
    if not 0.0 <= base_u < ident_u:
        raise SystemExit(
            f"expected first-sentence baseline ({base_u}) to sit below identity ({ident_u})"
        )
    print(
        f"\nOK: first-sentence unigram F1={base_u} < identity {ident_u}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
