"""Per-article hop ledger: retention, ROUGE, compression, OOVs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from .entities import missing_mentions, present_mentions, retention_ratio
from .hops import HopRecord
from .metrics import compression_ratio, rouge_scores
from .packing import packing_stats


@dataclass
class LedgerRow:
    article_id: str
    hop: str
    n_words: int
    compression_vs_source: float
    entity_retention: float
    entities_kept: List[str]
    entities_lost: List[str]
    rouge1_vs_gold_da: float | None
    rougeL_vs_gold_da: float | None
    extra: Dict[str, float | int | str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        row = {
            "article_id": self.article_id,
            "hop": self.hop,
            "n_words": self.n_words,
            "compression_vs_source": round(self.compression_vs_source, 4),
            "entity_retention": round(self.entity_retention, 4),
            "entities_kept": ";".join(self.entities_kept),
            "entities_lost": ";".join(self.entities_lost),
            "rouge1_vs_gold_da": (
                None if self.rouge1_vs_gold_da is None else round(self.rouge1_vs_gold_da, 4)
            ),
            "rougeL_vs_gold_da": (
                None if self.rougeL_vs_gold_da is None else round(self.rougeL_vs_gold_da, 4)
            ),
        }
        row.update(self.extra)
        return row


def _word_count(text: str) -> int:
    from .tokenize import lowercase_words

    return len(lowercase_words(text))


def _row(
    record: HopRecord,
    hop: str,
    text: str,
    gold_entities: Sequence[str],
    score_against_gold: bool,
) -> LedgerRow:
    rouge = rouge_scores(text, record.gold_da_summary) if score_against_gold else None
    return LedgerRow(
        article_id=record.article_id,
        hop=hop,
        n_words=_word_count(text),
        compression_vs_source=compression_ratio(record.danish_source, text),
        entity_retention=retention_ratio(text, gold_entities),
        entities_kept=present_mentions(text, gold_entities),
        entities_lost=missing_mentions(text, gold_entities),
        rouge1_vs_gold_da=None if rouge is None else rouge.rouge1,
        rougeL_vs_gold_da=None if rouge is None else rouge.rougeL,
    )


def build_ledger(record: HopRecord, gold_entities: Sequence[str]) -> List[LedgerRow]:
    """One row per hop that a human would stare at in a lab notebook."""
    stats = packing_stats(record.windows)
    rows = [
        _row(record, "da_source", record.danish_source, gold_entities, False),
        _row(record, "en_oracle", record.english_oracle, gold_entities, False),
        _row(record, "en_gloss", record.english_gloss, gold_entities, False),
        _row(record, "en_summary_oracle", record.english_summary_oracle, gold_entities, False),
        _row(record, "en_summary_gloss", record.english_summary_gloss, gold_entities, False),
        _row(record, "da_back_oracle", record.danish_back_oracle, gold_entities, True),
        _row(record, "da_back_gloss", record.danish_back_gloss, gold_entities, True),
        _row(record, "gold_da_summary", record.gold_da_summary, gold_entities, True),
    ]
    rows[0].extra = {
        "n_windows": stats["n_windows"],
        "pack_mean_budget": round(stats["mean_budget"], 2),
        "gloss_coverage_da": round(record.gloss_coverage_da, 4),
        "gloss_coverage_en": round(record.gloss_coverage_en, 4),
        "n_oov_da": len(record.gloss_unknown_da),
        "n_oov_en": len(record.gloss_unknown_en),
    }
    return rows


def summarise_ledger(rows: Sequence[LedgerRow]) -> Dict[str, float]:
    """Mean retention / ROUGE for the two Danish back-translations."""
    back_oracle = [r for r in rows if r.hop == "da_back_oracle"]
    back_gloss = [r for r in rows if r.hop == "da_back_gloss"]

    def _mean(items: Sequence[LedgerRow], attr: str) -> float:
        vals = [getattr(i, attr) for i in items if getattr(i, attr) is not None]
        if not vals:
            return 0.0
        return sum(vals) / len(vals)

    return {
        "oracle_entity_retention": _mean(back_oracle, "entity_retention"),
        "gloss_entity_retention": _mean(back_gloss, "entity_retention"),
        "oracle_rouge1": _mean(back_oracle, "rouge1_vs_gold_da"),
        "gloss_rouge1": _mean(back_gloss, "rouge1_vs_gold_da"),
        "oracle_rougeL": _mean(back_oracle, "rougeL_vs_gold_da"),
        "gloss_rougeL": _mean(back_gloss, "rougeL_vs_gold_da"),
        "oracle_compression": _mean(back_oracle, "compression_vs_source"),
        "gloss_compression": _mean(back_gloss, "compression_vs_source"),
    }
