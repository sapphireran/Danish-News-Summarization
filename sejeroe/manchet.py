"""Inverted-pyramid / manchet coverage.

A Danish news manchet is the first sentence (sometimes the first two) that
should carry WHO, WHAT, WHEN and WHERE. The 2023 T5 hop is applied to
*packed English windows*, then concatenated. That can invent a second-sentence
lede or push WHEN into a trailing clause that later hops drop.

This module scores the first sentence of a text against the gold slot card.
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.models import Article
from sejeroe.normalize import contains_phrase
from sejeroe.sentences import first_sentence

LEDE_SLOTS = ("who", "what", "when", "where")


@dataclass(frozen=True)
class ManchetScore:
    article_id: str
    text_role: str
    lead: str
    hits: tuple[str, ...]
    misses: tuple[str, ...]

    @property
    def coverage(self) -> float:
        total = len(LEDE_SLOTS)
        return len(self.hits) / total if total else 0.0

    @property
    def is_full_lede(self) -> bool:
        return len(self.misses) == 0


def score_manchet(article: Article, text: str, text_role: str) -> ManchetScore:
    lead = first_sentence(text)
    hits: list[str] = []
    misses: list[str] = []
    for name in LEDE_SLOTS:
        forms = article.slots.surface_forms(name)
        if any(contains_phrase(lead, form) for form in forms):
            hits.append(name)
        else:
            misses.append(name)
    return ManchetScore(
        article_id=article.id,
        text_role=text_role,
        lead=lead,
        hits=tuple(hits),
        misses=tuple(misses),
    )
