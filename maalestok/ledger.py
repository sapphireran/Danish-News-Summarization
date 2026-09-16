"""Per-article and corpus-level survival of measures across hops."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .article import Article
from .hops import HopPair, align_measures
from .measures import extract_measures

HOP_FIELDS = ("pivot_en", "summary_en", "silver_da", "oracle_da", "lead2_da")


@dataclass(frozen=True)
class ArticleLedger:
    article_id: str
    title: str
    source_count: int
    pairs: dict[str, tuple[HopPair, ...]]

    def survival(self, hop: str) -> float:
        pairs = [p for p in self.pairs[hop] if p.label != "hallucinated"]
        if not pairs:
            return 0.0
        ok = sum(1 for p in pairs if p.label == "ok")
        return ok / len(pairs)

    def planted_caught(self, article: Article) -> list[str]:
        """Return planted codes that appear as non-ok silver labels."""
        silver_labels = {p.label for p in self.pairs["silver_da"] if p.label != "ok"}
        return [err.code for err in article.planted if err.code in silver_labels]


@dataclass(frozen=True)
class CorpusLedger:
    articles: tuple[ArticleLedger, ...]

    def mean_survival(self, hop: str) -> float:
        if not self.articles:
            return 0.0
        return sum(row.survival(hop) for row in self.articles) / len(self.articles)

    def worst(self, hop: str = "silver_da") -> ArticleLedger:
        return min(self.articles, key=lambda row: row.survival(hop))


def build_article_ledger(article: Article) -> ArticleLedger:
    source = extract_measures(article.body_da)
    pairs = {
        hop: tuple(align_measures(source, extract_measures(getattr(article, hop))))
        for hop in HOP_FIELDS
    }
    return ArticleLedger(
        article_id=article.id,
        title=article.title,
        source_count=len(source),
        pairs=pairs,
    )


def build_corpus_ledger(articles: Iterable[Article]) -> CorpusLedger:
    return CorpusLedger(tuple(build_article_ledger(article) for article in articles))
