"""Pair hand-parallel Danish and English sentences.

The 2023 ``translate.py`` hop does not emit sentence alignments. The Sejerø
bodies were written as matched sentences so the desk can show length
inflation *inside* a brief, not only on the whole article. A quote sentence
is flagged because that is the hop ``summary.py`` most often drops.
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.models import Article
from sejeroe.normalize import contains_phrase
from sejeroe.sentences import split_sentences
from sejeroe.tokenize import LengthNotion, measure


@dataclass(frozen=True)
class AlignedSentence:
    index: int
    danish: str
    english: str
    da_words: int
    en_words: int
    da_subwords: int
    en_subwords: int
    is_quote: bool

    @property
    def word_ratio(self) -> float:
        if self.da_words == 0:
            return 0.0
        return self.en_words / self.da_words

    @property
    def subword_ratio(self) -> float:
        if self.da_subwords == 0:
            return 0.0
        return self.en_subwords / self.da_subwords


@dataclass(frozen=True)
class Alignment:
    article_id: str
    pairs: tuple[AlignedSentence, ...]
    leftover_da: tuple[str, ...]
    leftover_en: tuple[str, ...]

    @property
    def aligned(self) -> bool:
        return not self.leftover_da and not self.leftover_en

    @property
    def quote_index(self) -> int | None:
        for pair in self.pairs:
            if pair.is_quote:
                return pair.index
        return None


def align_article(article: Article) -> Alignment:
    danish = split_sentences(article.body_da)
    english = split_sentences(article.body_en)
    n = min(len(danish), len(english))
    pairs: list[AlignedSentence] = []
    for index in range(n):
        da = danish[index]
        en = english[index]
        is_quote = any(
            contains_phrase(da, quote.danish) or contains_phrase(en, quote.english)
            for quote in article.quotes
        )
        pairs.append(
            AlignedSentence(
                index=index,
                danish=da,
                english=en,
                da_words=measure(da, LengthNotion.WORDS),
                en_words=measure(en, LengthNotion.WORDS),
                da_subwords=measure(da, LengthNotion.ROUGH_SUBWORD),
                en_subwords=measure(en, LengthNotion.ROUGH_SUBWORD),
                is_quote=is_quote,
            )
        )
    return Alignment(
        article_id=article.id,
        pairs=tuple(pairs),
        leftover_da=tuple(danish[n:]),
        leftover_en=tuple(english[n:]),
    )
