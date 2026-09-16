"""Gold figures (clocks, counts, kroner) that a manchet should not invent."""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.models import Article
from sejeroe.normalize import contains_phrase


@dataclass(frozen=True)
class FigureHit:
    figure: str
    in_text: bool


@dataclass(frozen=True)
class FigureScore:
    article_id: str
    text_role: str
    hits: tuple[FigureHit, ...]

    @property
    def kept(self) -> int:
        return sum(1 for hit in self.hits if hit.in_text)

    @property
    def total(self) -> int:
        return len(self.hits)

    @property
    def recall(self) -> float:
        if not self.hits:
            return 0.0
        return self.kept / self.total

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(hit.figure for hit in self.hits if not hit.in_text)


def score_figures(article: Article, text: str, text_role: str) -> FigureScore:
    hits = tuple(
        FigureHit(figure=item, in_text=contains_phrase(text, item))
        for item in article.figures
    )
    return FigureScore(article_id=article.id, text_role=text_role, hits=hits)
