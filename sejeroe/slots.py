"""5W1H slot cards and surface-form recall.

A silver summary can keep a high unigram overlap and still drop WHEN from
the manchet, swap WHO, or flip WHY. Slot recall is a tiny closed-world
check: did any gold surface form survive in the text we are scoring?
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.models import SLOT_NAMES, Article, SlotCard
from sejeroe.normalize import contains_phrase


@dataclass(frozen=True)
class SlotHit:
    name: str
    hit: bool
    matched: str | None


@dataclass(frozen=True)
class SlotScore:
    article_id: str
    text_role: str
    hits: tuple[SlotHit, ...]

    @property
    def recall(self) -> float:
        if not self.hits:
            return 0.0
        return sum(1 for hit in self.hits if hit.hit) / len(self.hits)

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(hit.name for hit in self.hits if not hit.hit)


def score_slots(card: SlotCard, text: str, article_id: str, text_role: str) -> SlotScore:
    hits: list[SlotHit] = []
    for name in SLOT_NAMES:
        matched = None
        for form in card.surface_forms(name):
            if contains_phrase(text, form):
                matched = form
                break
        hits.append(SlotHit(name=name, hit=matched is not None, matched=matched))
    return SlotScore(article_id=article_id, text_role=text_role, hits=tuple(hits))


def score_article_roles(article: Article) -> dict[str, SlotScore]:
    roles = {
        "body_da": article.body_da,
        "summary_en": article.summary_en,
        "summary_da": article.summary_da,
        "oracle_da": article.oracle_da,
    }
    return {
        role: score_slots(article.slots, text, article.id, role)
        for role, text in roles.items()
    }
