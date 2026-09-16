"""Deterministic DA↔EN stand-in used by the dry-run examples.

This is not a translation model. It applies longest-first phrase substitutions
from a bilingual glossary so the four pipeline stages stay readable without
OPUS-MT or a GPU. Unknown tokens are left unchanged, which is intentional:
the examples should show what the *pipeline* does to windows, not pretend to
be Helsinki-NLP.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property

# Phrase table is written longest-first at lookup time. Keep multi-word
# expressions here; single-word fallbacks live in WORD_PAIRS.
PHRASE_PAIRS: tuple[tuple[str, str], ...] = (
    ("den nye indre havn", "the new inner harbour"),
    ("nordjyllands historiske museum", "the historical museum of north jutland"),
    ("aalborg historiske museum", "aalborg historical museum"),
    ("det gamle bibliotek", "the old library"),
    ("den kommunale forvaltning", "the municipal administration"),
    ("kommunalbestyrelsen vedtog", "the city council adopted"),
    ("kommunalbestyrelsen", "the city council"),
    ("et flertal i byrådet", "a majority on the city council"),
    ("havnefronten i aalborg", "the waterfront in aalborg"),
    ("havnefronten", "the waterfront"),
    ("offentlig høring", "public consultation"),
    ("offentlige høring", "public consultation"),
    ("grøn omstilling", "green transition"),
    ("havvindmøllepark", "offshore wind farm"),
    ("havvindmøller", "offshore wind turbines"),
    ("vedvarende energi", "renewable energy"),
    ("superligaen", "the danish superliga"),
    ("aaB vandt", "aab won"),
    ("færgeafgangen", "the ferry departure"),
    ("færgeoverfarten", "the ferry crossing"),
    ("strejken blandt", "the strike among"),
    ("efter flere dages regn", "after several days of rain"),
    ("ifølge kommunen", "according to the municipality"),
    ("ifølge politiet", "according to the police"),
    ("ifølge forskerne", "according to the researchers"),
    ("ifølge museet", "according to the museum"),
    ("ifølge klubben", "according to the club"),
    ("millioner kroner", "million kroner"),
    ("mia. kr.", "billion kroner"),
    ("mio. kr.", "million kroner"),
    ("f.eks.", "for example"),
    ("bl.a.", "among other things"),
    ("osv.", "and so on"),
    ("dvs.", "that is"),
    ("pga.", "because of"),
    ("hhv.", "respectively"),
    ("kl.", "at"),
    ("nr.", "no."),
    ("ca.", "approximately"),
)

WORD_PAIRS: tuple[tuple[str, str], ...] = (
    ("aalborg", "aalborg"),
    ("aarhus", "aarhus"),
    ("artikel", "article"),
    ("biblioteket", "the library"),
    ("bibliotek", "library"),
    ("budgettet", "the budget"),
    ("budget", "budget"),
    ("byrådet", "the city council"),
    ("byen", "the city"),
    ("børn", "children"),
    ("dag", "day"),
    ("dage", "days"),
    ("de", "the"),
    ("den", "the"),
    ("det", "the"),
    ("en", "a"),
    ("et", "a"),
    ("færgen", "the ferry"),
    ("færge", "ferry"),
    ("forskere", "researchers"),
    ("havnen", "the harbour"),
    ("havn", "harbour"),
    ("i", "in"),
    ("og", "and"),
    ("kommunen", "the municipality"),
    ("kommune", "municipality"),
    ("kroner", "kroner"),
    ("kultur", "culture"),
    ("museet", "the museum"),
    ("museum", "museum"),
    ("ny", "new"),
    ("nye", "new"),
    ("planen", "the plan"),
    ("plan", "plan"),
    ("politiet", "the police"),
    ("regn", "rain"),
    ("regnen", "the rain"),
    ("strejke", "strike"),
    ("strejken", "the strike"),
    ("udstilling", "exhibition"),
    ("udstillingen", "the exhibition"),
    ("vejr", "weather"),
    ("vejret", "the weather"),
    ("vind", "wind"),
    ("vinden", "the wind"),
    ("åbner", "opens"),
    ("åbnede", "opened"),
    ("åbning", "opening"),
)


_WORD = re.compile(r"[A-Za-zÆØÅæøå0-9]+(?:-[A-Za-zÆØÅæøå0-9]+)*|[^\sA-Za-zÆØÅæøå0-9]+|\s+")


def _lower(text: str) -> str:
    return text.casefold()


def _apply_casing(source: str, translated: str) -> str:
    if source.isupper():
        return translated.upper()
    if source[:1].isupper():
        return translated[:1].upper() + translated[1:]
    return translated


@dataclass(frozen=True)
class GlossaryBackend:
    """Phrase-table backend that implements the `pipeline.Backend` protocol."""

    extra_phrases: tuple[tuple[str, str], ...] = ()

    @cached_property
    def _forward(self) -> list[tuple[str, str]]:
        pairs = tuple(PHRASE_PAIRS) + self.extra_phrases + tuple(WORD_PAIRS)
        return sorted(pairs, key=lambda pair: len(pair[0]), reverse=True)

    @cached_property
    def _backward(self) -> list[tuple[str, str]]:
        pairs = tuple((en, da) for da, en in PHRASE_PAIRS + self.extra_phrases + WORD_PAIRS)
        return sorted(pairs, key=lambda pair: len(pair[0]), reverse=True)

    def translate_da_en(self, sentences: list[str]) -> list[str]:
        return [self._translate(sentence, self._forward) for sentence in sentences]

    def translate_en_da(self, sentences: list[str]) -> list[str]:
        return [self._translate(sentence, self._backward) for sentence in sentences]

    def summarize_en(self, text: str) -> str:
        """Keep the first two sentences; fall back to the first 24 words."""
        from danish_news.chunking import split_sentences

        sentences = split_sentences(text)
        if not sentences:
            return ""
        if len(sentences) == 1:
            words = text.split()
            return " ".join(words[:24]).rstrip(" ,;") + ("." if words else "")
        return " ".join(sentences[:2])

    def _translate(self, text: str, table: list[tuple[str, str]]) -> str:
        if not text:
            return ""
        remaining = text
        out: list[str] = []
        while remaining:
            match = self._longest_prefix(remaining, table)
            if match is None:
                token, remaining = _next_token(remaining)
                out.append(token)
                continue
            source, target, consumed = match
            out.append(_apply_casing(source, target))
            remaining = remaining[consumed:]
        return _cleanup("".join(out))

    def _longest_prefix(
        self, text: str, table: list[tuple[str, str]]
    ) -> tuple[str, str, int] | None:
        folded = _lower(text)
        for source, target in table:
            if not folded.startswith(_lower(source)):
                continue
            consumed = len(source)
            # Do not match inside a longer word: `havn` must not eat `havnen`
            # unless the glossary also lists `havnen`.
            if consumed < len(text) and text[consumed].isalpha():
                continue
            return text[:consumed], target, consumed
        return None


def _next_token(text: str) -> tuple[str, str]:
    match = _WORD.match(text)
    if not match:
        return text[:1], text[1:]
    return match.group(0), text[match.end() :]


def _cleanup(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text.strip()
