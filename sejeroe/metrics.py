"""Toy overlap metrics plus the desk scores.

The 2023 trainer reports ROUGE-1/2/L mid F-measure via
``datasets.load_metric('rouge')``. That metric is n-gram overlap. It is
almost blind to a WHO swap that keeps the rest of the lede, and it can
score a polarity flip on WHY as a mild unigram miss.

This module keeps a tiny ROUGE-shaped scorer so the workbook can sit next
to a slot F1 without downloading ``rouge_score``.
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.connectives import ConnectiveScore, score_connectives
from sejeroe.manchet import ManchetScore, score_manchet
from sejeroe.models import Article
from sejeroe.normalize import fold
from sejeroe.quotes import QuoteScore, score_article_quotes
from sejeroe.slots import SlotScore, score_slots
from sejeroe.tokenize import words


def _ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0 or len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


@dataclass(frozen=True)
class OverlapScore:
    rouge1_f: float
    rouge2_f: float
    rougel_f: float


def _lcs_len(left: list[str], right: list[str]) -> int:
    if not left or not right:
        return 0
    prev = [0] * (len(right) + 1)
    for token in left:
        current = [0]
        for j, other in enumerate(right, start=1):
            if token == other:
                current.append(prev[j - 1] + 1)
            else:
                current.append(max(prev[j], current[-1]))
        prev = current
    return prev[-1]


def overlap(prediction: str, reference: str) -> OverlapScore:
    pred = words(fold(prediction))
    ref = words(fold(reference))
    if not pred or not ref:
        return OverlapScore(0.0, 0.0, 0.0)

    def ngram_f(n: int) -> float:
        pred_n = _ngrams(pred, n)
        ref_n = _ngrams(ref, n)
        if not pred_n or not ref_n:
            return 0.0
        ref_counts: dict[tuple[str, ...], int] = {}
        for gram in ref_n:
            ref_counts[gram] = ref_counts.get(gram, 0) + 1
        overlap_n = 0
        for gram in pred_n:
            if ref_counts.get(gram, 0) > 0:
                overlap_n += 1
                ref_counts[gram] -= 1
        precision = overlap_n / len(pred_n)
        recall = overlap_n / len(ref_n)
        return _f1(precision, recall)

    lcs = _lcs_len(pred, ref)
    rouge_l = _f1(lcs / len(pred), lcs / len(ref))
    return OverlapScore(rouge1_f=ngram_f(1), rouge2_f=ngram_f(2), rougel_f=rouge_l)


@dataclass(frozen=True)
class DeskRow:
    article_id: str
    split: str
    text_role: str
    slot_recall: float
    missing_slots: tuple[str, ...]
    manchet_coverage: float
    manchet_misses: tuple[str, ...]
    quotes_kept: int
    quotes_total: int
    connectives_kept: int
    connectives_total: int
    rouge1_vs_oracle: float
    rouge1_vs_silver: float


def _desk_row(
    article: Article,
    text: str,
    text_role: str,
    slots: SlotScore,
    manchet: ManchetScore,
    quotes: tuple[QuoteScore, ...],
    connectives: tuple[ConnectiveScore, ...],
) -> DeskRow:
    return DeskRow(
        article_id=article.id,
        split=article.split,
        text_role=text_role,
        slot_recall=slots.recall,
        missing_slots=slots.missing,
        manchet_coverage=manchet.coverage,
        manchet_misses=manchet.misses,
        quotes_kept=sum(1 for item in quotes if item.kept),
        quotes_total=len(quotes),
        connectives_kept=sum(1 for item in connectives if item.hit),
        connectives_total=len(connectives),
        rouge1_vs_oracle=overlap(text, article.oracle_da).rouge1_f,
        rouge1_vs_silver=overlap(text, article.summary_da).rouge1_f,
    )


def score_text(article: Article, text: str, text_role: str) -> DeskRow:
    slots = score_slots(article.slots, text, article.id, text_role)
    manchet = score_manchet(article, text, text_role)
    quotes = score_article_quotes(article, text, text_role)
    connectives = score_connectives(article, text, text_role)
    return _desk_row(article, text, text_role, slots, manchet, quotes, connectives)


def score_article(article: Article) -> tuple[DeskRow, ...]:
    roles = (
        ("summary_da", article.summary_da),
        ("oracle_da", article.oracle_da),
        ("summary_en", article.summary_en),
    )
    rows = [score_text(article, text, role) for role, text in roles]
    for error in article.planted:
        rows.append(score_text(article, error.summary_da, f"planted:{error.kind}"))
    return tuple(rows)


def planted_blind_spots(article: Article) -> list[dict[str, object]]:
    """Rows where overlap stays high while a planted slot disappears."""
    rows: list[dict[str, object]] = []
    silver = score_text(article, article.summary_da, "summary_da")
    for error in article.planted:
        planted = score_text(article, error.summary_da, f"planted:{error.kind}")
        rows.append(
            {
                "article_id": article.id,
                "kind": error.kind,
                "note": error.note,
                "silver_slot_recall": round(silver.slot_recall, 3),
                "planted_slot_recall": round(planted.slot_recall, 3),
                "silver_rouge1_vs_silver": round(silver.rouge1_vs_silver, 3),
                "planted_rouge1_vs_silver": round(planted.rouge1_vs_silver, 3),
                "planted_missing_slots": ",".join(planted.missing_slots),
                "intended_drops": ",".join(error.dropped_slots),
            }
        )
    return rows
