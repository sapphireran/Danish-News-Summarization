"""Entity-survival ledger across the five Kystlinje texts."""

from __future__ import annotations

from dataclasses import dataclass, field

from .corpus import Brief, all_briefs
from .danish import lead_n
from .entities import Entity, entity_survives, extract_entities, unique_by_key

HOPS = ("source", "pivot", "summary", "silver", "lead2")


@dataclass(frozen=True)
class EntityRow:
    entity: Entity
    present: dict[str, bool]

    def survived(self, hop: str) -> bool:
        return self.present.get(hop, False)


@dataclass
class HopLedger:
    brief: Brief
    rows: list[EntityRow] = field(default_factory=list)

    def source_entities(self) -> list[Entity]:
        return [row.entity for row in self.rows]

    def count(self, hop: str) -> int:
        return sum(1 for row in self.rows if row.survived(hop))

    def lost_between(self, start: str, end: str) -> list[Entity]:
        lost: list[Entity] = []
        for row in self.rows:
            if row.survived(start) and not row.survived(end):
                lost.append(row.entity)
        return lost

    def survival_rate(self, hop: str) -> float:
        if not self.rows:
            return 0.0
        return self.count(hop) / len(self.rows)

    def texts(self) -> dict[str, str]:
        return {
            "source": self.brief.body_da,
            "pivot": self.brief.pivot_en,
            "summary": self.brief.summary_en,
            "silver": self.brief.silver_da,
            "lead2": lead_n(self.brief.body_da, 2),
        }


def build_ledger(brief: Brief) -> HopLedger:
    texts = {
        "source": brief.body_da,
        "pivot": brief.pivot_en,
        "summary": brief.summary_en,
        "silver": brief.silver_da,
        "lead2": lead_n(brief.body_da, 2),
    }
    source_entities = unique_by_key(extract_entities(brief.body_da, article_id=brief.id))
    rows: list[EntityRow] = []
    for ent in source_entities:
        present = {hop: entity_survives(ent, texts[hop]) for hop in HOPS}
        present["source"] = True
        rows.append(EntityRow(entity=ent, present=present))
    return HopLedger(brief=brief, rows=rows)


def build_all_ledgers() -> list[HopLedger]:
    return [build_ledger(brief) for brief in all_briefs()]


def mean_survival(ledgers: list[HopLedger], hop: str) -> float:
    if not ledgers:
        return 0.0
    return sum(led.survival_rate(hop) for led in ledgers) / len(ledgers)


def mean_lost(ledgers: list[HopLedger], start: str, end: str) -> float:
    if not ledgers:
        return 0.0
    return sum(len(led.lost_between(start, end)) for led in ledgers) / len(ledgers)


def worst_end_to_end(ledgers: list[HopLedger]) -> HopLedger:
    return min(ledgers, key=lambda led: (led.survival_rate("silver"), led.brief.id))


def hop_loss_table(ledgers: list[HopLedger]) -> list[tuple[str, str, float]]:
    """Average entities lost on each directed hop."""
    pairs = (("source", "pivot"), ("pivot", "summary"), ("summary", "silver"))
    return [(a, b, mean_lost(ledgers, a, b)) for a, b in pairs]


def kind_survival(ledgers: list[HopLedger], kind: str, hop: str) -> float:
    rows = [row for led in ledgers for row in led.rows if row.entity.kind == kind]
    if not rows:
        return 0.0
    return sum(1 for row in rows if row.survived(hop)) / len(rows)
