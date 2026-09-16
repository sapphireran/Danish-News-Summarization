"""Danish / English length inflation.

Danish news compounds (``færgeafgang``, ``søndagslukning``, ``kirketag``)
are one whitespace word and several subword pieces. The English gloss is
usually several words. Packing on a *word* budget therefore treats the
Danish body as shorter than the English hop, while a rough subword budget
moves them closer together. That mismatch is one reason ``translate.py``
and ``summary.py`` can open a different number of windows on the same brief.
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.models import Article
from sejeroe.tokenize import LengthNotion, measure, words


# Compounds written as one Danish token in the Sejerø briefs.
COMPOUNDS = (
    "færgeafgang",
    "Sejerøfærgen",
    "SMS-varslingen",
    "færgelejet",
    "jomfruhummere",
    "kystmøller",
    "søkablet",
    "industrihorisont",
    "novemberomsætningen",
    "søndagsvagter",
    "søndagslukning",
    "tankvogn",
    "ø-indsamling",
    "kirketag",
    "menighedsrådet",
    "sideindgangen",
    "præstegården",
    "sandbanken",
    "Naturstyrelsen",
)


@dataclass(frozen=True)
class LengthPair:
    article_id: str
    notion: str
    danish: int
    english: int

    @property
    def ratio(self) -> float:
        if self.danish == 0:
            return 0.0
        return self.english / self.danish


def pair_lengths(article: Article, notion: LengthNotion) -> LengthPair:
    return LengthPair(
        article_id=article.id,
        notion=notion.value,
        danish=measure(article.body_da, notion),
        english=measure(article.body_en, notion),
    )


def compound_hits(text: str) -> tuple[str, ...]:
    folded = text.lower()
    found = [item for item in COMPOUNDS if item.lower() in folded]
    return tuple(found)


def compound_table(article: Article) -> list[dict[str, object]]:
    rows = []
    for item in compound_hits(article.body_da):
        rows.append(
            {
                "article_id": article.id,
                "compound": item,
                "da_words": 1,
                "da_subwords": measure(item, LengthNotion.ROUGH_SUBWORD),
                "en_body_words": len(words(article.body_en)),
            }
        )
    return rows
