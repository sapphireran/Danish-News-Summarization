"""Extractive lede baselines.

A Danish news manchet is already a summary. Before blaming T5, the desk
asks whether *copying the first sentence* (and the first two) beats the
silver label on slot coverage. The 2023 scripts never reported that
baseline: ``eval.py`` only scores a fine-tuned mT5 against Nordjylland.
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.metrics import DeskRow, score_text
from sejeroe.models import Article
from sejeroe.sentences import split_sentences


def extractive_lede(text: str, n: int) -> str:
    if n < 1:
        raise ValueError("n must be >= 1")
    sentences = split_sentences(text)
    return " ".join(sentences[:n]).strip()


@dataclass(frozen=True)
class BaselineRow:
    article_id: str
    name: str
    text: str
    desk: DeskRow

    @property
    def manchet(self) -> float:
        return self.desk.manchet_coverage

    @property
    def slots(self) -> float:
        return self.desk.slot_recall


def baselines_for(article: Article) -> tuple[BaselineRow, ...]:
    specs = (
        ("lead1_da", extractive_lede(article.body_da, 1)),
        ("lead2_da", extractive_lede(article.body_da, 2)),
        ("silver_da", article.summary_da),
        ("oracle_da", article.oracle_da),
    )
    return tuple(
        BaselineRow(
            article_id=article.id,
            name=name,
            text=text,
            desk=score_text(article, text, name),
        )
        for name, text in specs
    )


def comparison_table(article: Article) -> dict[str, object]:
    rows = {item.name: item for item in baselines_for(article)}
    lead1 = rows["lead1_da"]
    silver = rows["silver_da"]
    return {
        "article_id": article.id,
        "lead1_manchet": round(lead1.manchet, 3),
        "silver_manchet": round(silver.manchet, 3),
        "oracle_manchet": round(rows["oracle_da"].manchet, 3),
        "lead1_slots": round(lead1.slots, 3),
        "lead2_slots": round(rows["lead2_da"].slots, 3),
        "silver_slots": round(silver.slots, 3),
        "lead1_r1_oracle": round(lead1.desk.rouge1_vs_oracle, 3),
        "silver_r1_oracle": round(silver.desk.rouge1_vs_oracle, 3),
        "lead1_beats_silver_manchet": lead1.manchet > silver.manchet,
        "lead1_beats_silver_slots": lead1.slots > silver.slots,
        "lead2_beats_silver_slots": rows["lead2_da"].slots > silver.slots,
    }
