"""Quote and attribution survival.

The English T5 news hop in ``summary.py`` is extractive-adjacent and often
keeps a lede while dropping the quoted clause. Back-translation then loses
the Danish quotation marks. The desk checks both the span and the cue
(``siger`` / ``said``) plus the speaker.
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.models import Article, Quote
from sejeroe.normalize import contains_phrase, fold
from sejeroe.tokenize import words


@dataclass(frozen=True)
class QuoteScore:
    article_id: str
    speaker: str
    text_role: str
    span_hit: bool
    speaker_hit: bool
    cue_hit: bool
    token_overlap: float

    @property
    def kept(self) -> bool:
        return self.span_hit or (self.speaker_hit and self.token_overlap >= 0.45)


def _overlap(quote_text: str, haystack: str) -> float:
    quote_tokens = set(words(fold(quote_text)))
    hay_tokens = set(words(fold(haystack)))
    if not quote_tokens:
        return 0.0
    return len(quote_tokens & hay_tokens) / len(quote_tokens)


def score_quote(quote: Quote, text: str, article_id: str, text_role: str) -> QuoteScore:
    danishish = text_role.endswith("_da") or text_role.endswith("da")
    span = quote.danish if danishish else quote.english
    cue = quote.cue_da if danishish else quote.cue_en
    # Silver Danish often keeps the English cue wording after a clumsy hop.
    cue_hit = contains_phrase(text, cue) or contains_phrase(text, quote.cue_da) or contains_phrase(
        text, quote.cue_en
    )
    return QuoteScore(
        article_id=article_id,
        speaker=quote.speaker,
        text_role=text_role,
        span_hit=contains_phrase(text, span),
        speaker_hit=contains_phrase(text, quote.speaker),
        cue_hit=cue_hit,
        token_overlap=_overlap(span, text),
    )


def score_article_quotes(article: Article, text: str, text_role: str) -> tuple[QuoteScore, ...]:
    return tuple(score_quote(quote, text, article.id, text_role) for quote in article.quotes)
