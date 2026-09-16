"""Discourse connective survival.

Island briefs in this workbook lean on ``hvis``, ``men``, ``fordi`` and
``ifølge``. Those words are easy for a translator and easy for a summarizer
to drop. Losing ``men`` often erases the contrast the manchet was built on.
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.models import Article
from sejeroe.normalize import contains_phrase


@dataclass(frozen=True)
class ConnectiveScore:
    article_id: str
    text_role: str
    connective: str
    hit: bool


def score_connectives(article: Article, text: str, text_role: str) -> tuple[ConnectiveScore, ...]:
    return tuple(
        ConnectiveScore(
            article_id=article.id,
            text_role=text_role,
            connective=item,
            hit=contains_phrase(text, item),
        )
        for item in article.connectives_da
    )
