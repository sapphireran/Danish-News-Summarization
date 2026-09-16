"""Night-editor gates for a Sejerø brief.

These are not ROUGE. They are the checks a small-island paper would run
before putting a silver label on the wire: does the manchet still name
the actor and the event, is the clock nearby, did the quote survive, and
were the figures left alone?
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.figures import score_figures
from sejeroe.manchet import score_manchet
from sejeroe.models import Article
from sejeroe.normalize import contains_phrase
from sejeroe.quotes import score_article_quotes
from sejeroe.sentences import split_sentences
from sejeroe.slots import score_slots


@dataclass(frozen=True)
class Gate:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Stylebook:
    article_id: str
    text_role: str
    gates: tuple[Gate, ...]

    @property
    def passed(self) -> int:
        return sum(1 for gate in self.gates if gate.passed)

    @property
    def total(self) -> int:
        return len(self.gates)

    @property
    def failed(self) -> tuple[str, ...]:
        return tuple(gate.name for gate in self.gates if not gate.passed)

    @property
    def ok(self) -> bool:
        return self.total > 0 and self.passed == self.total


def _first_two(text: str) -> str:
    return " ".join(split_sentences(text)[:2])


def grade(article: Article, text: str, text_role: str) -> Stylebook:
    manchet = score_manchet(article, text, text_role)
    slots = score_slots(article.slots, text, article.id, text_role)
    quotes = score_article_quotes(article, text, text_role)
    figures = score_figures(article, text, text_role)
    opening = _first_two(text)
    when_forms = article.slots.surface_forms("when")
    where_forms = article.slots.surface_forms("where")
    when_near = any(contains_phrase(opening, form) for form in when_forms)
    where_near = any(contains_phrase(opening, form) for form in where_forms)
    quote_ok = any(item.kept for item in quotes) or any(
        contains_phrase(text, quote.speaker) for quote in article.quotes
    )
    contrast = "men" in {item.lower() for item in article.connectives_da}
    men_hit = contains_phrase(text, "men") if contrast else True

    gates = (
        Gate(
            "who_in_lede",
            "who" in manchet.hits,
            "WHO in the first sentence" if "who" in manchet.hits else f"lede misses WHO: {manchet.lead}",
        ),
        Gate(
            "what_in_lede",
            "what" in manchet.hits,
            "WHAT in the first sentence" if "what" in manchet.hits else "lede misses WHAT",
        ),
        Gate(
            "when_in_opening",
            when_near,
            "WHEN in the first two sentences" if when_near else f"WHEN missing from opening; slot missing={slots.missing}",
        ),
        Gate(
            "where_in_opening",
            where_near,
            "WHERE in the first two sentences" if where_near else "WHERE missing from opening",
        ),
        Gate(
            "quote_or_speaker",
            quote_ok,
            "quote or speaker present" if quote_ok else "quote span and speaker both gone",
        ),
        Gate(
            "figures_majority",
            figures.recall >= 0.5,
            f"figures {figures.kept}/{figures.total} missing={list(figures.missing) or '-'}",
        ),
        Gate(
            "contrast_men",
            men_hit,
            "contrast 'men' kept" if men_hit else "brief used 'men' and the text dropped it",
        ),
    )
    return Stylebook(article_id=article.id, text_role=text_role, gates=gates)


def grade_roles(article: Article) -> dict[str, Stylebook]:
    return {
        "lead1_da": grade(article, " ".join(split_sentences(article.body_da)[:1]), "lead1_da"),
        "silver_da": grade(article, article.summary_da, "silver_da"),
        "oracle_da": grade(article, article.oracle_da, "oracle_da"),
    }
