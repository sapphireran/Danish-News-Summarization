"""Named-entity and number tracking across silver-label hops.

The 2023 course never logged what survived DA→EN→summary→DA. This module
is the lab notebook that should have existed: given a gold entity list
(people, places, numbers) it records which hops still mention them.

Matching is deliberately fuzzy:

* case-insensitive
* hyphen / space / en-dash folding
* a gold mention matches if it appears as a substring of the hop text
  after folding, or if every content token of the mention appears

False positives are possible on short tokens (``Ø``, ``bus``). The
gazette uses long enough names that this stays usable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .tokenize import lowercase_words

_FOLD_RE = re.compile(r"[-\u2013\u2014\s]+")
_NUMBER_RE = re.compile(
    r"(?<![\w,])(\d+(?:[.,]\d+)*)(?![\w,])"
)

# Digit mentions should match Danish number words in the gazette.
# "4" is planted as *fire* in several stories; substring "4" would also
# falsely hit "14" and "06.00".
_DA_NUMBER_WORDS = {
    "0": ("0", "nul", "zero"),
    "1": ("1", "én", "ét", "one"),
    "2": ("2", "to", "two"),
    "3": ("3", "tre", "three"),
    "4": ("4", "fire", "four"),
    "5": ("5", "fem", "five"),
    "6": ("6", "seks", "six"),
    "7": ("7", "syv", "seven"),
    "8": ("8", "otte", "eight"),
    "9": ("9", "ni", "nine"),
    "10": ("10", "ti", "ten"),
    "12": ("12", "tolv", "twelve"),
    "14": ("14", "fourteen"),
    "15": ("15", "fifteen"),
    "17": ("17", "seventeen"),
    "18": ("18", "eighteen"),
    "20": ("20", "tyve", "twenty"),
    "25": ("25", "twenty-five"),
    "40": ("40", "forty"),
    "60": ("60", "sixty"),
    "65": ("65", "sixty-five"),
    "80": ("80", "eighty"),
    "87": ("87", "eighty-seven"),
}


@dataclass(frozen=True)
class EntityHit:
    mention: str
    present: bool
    folded: str


def fold(text: str) -> str:
    """Lowercase and collapse dashes/spaces so ``El-Khatib`` matches."""
    return _FOLD_RE.sub(" ", text.lower()).strip()


def extract_numbers(text: str) -> List[str]:
    return _NUMBER_RE.findall(text or "")


def _number_aliases(mention: str) -> tuple[str, ...]:
    folded = fold(mention)
    if folded in _DA_NUMBER_WORDS:
        return _DA_NUMBER_WORDS[folded]
    for digit, words in _DA_NUMBER_WORDS.items():
        if folded in words:
            return words
    return (folded,)


def _is_numeric_mention(mention: str) -> bool:
    compact = fold(mention).replace(".", "").replace(",", "")
    return compact.isdigit()


def mention_in_text(mention: str, text: str) -> bool:
    if not mention or not text:
        return False
    folded_mention = fold(mention)
    folded_text = fold(text)
    if not folded_mention:
        return False

    text_tokens = set(lowercase_words(text))
    number_tokens = {fold(n) for n in extract_numbers(text)}

    if _is_numeric_mention(mention):
        aliases = _number_aliases(mention)
        if any(a in text_tokens or a in number_tokens for a in aliases):
            return True
        # Allow exact numeric surface ("1,2", "06.00", "3. maj" is not purely numeric).
        return folded_mention in number_tokens

    if folded_mention in folded_text:
        return True
    tokens = lowercase_words(mention)
    if not tokens:
        return False
    alpha = [t for t in tokens if t.isalpha()]
    if alpha and all(t in text_tokens for t in alpha):
        return True
    return False


def extract_entities(text: str, gold: Sequence[str]) -> List[EntityHit]:
    return [
        EntityHit(mention=m, present=mention_in_text(m, text), folded=fold(m))
        for m in gold
        if m and m.strip()
    ]


def present_mentions(text: str, gold: Sequence[str]) -> List[str]:
    return [hit.mention for hit in extract_entities(text, gold) if hit.present]


def missing_mentions(text: str, gold: Sequence[str]) -> List[str]:
    return [hit.mention for hit in extract_entities(text, gold) if not hit.present]


def retention_ratio(text: str, gold: Sequence[str]) -> float:
    hits = extract_entities(text, gold)
    if not hits:
        return 1.0
    return sum(1 for h in hits if h.present) / len(hits)


def retention_table(
    hops: Sequence[tuple[str, str]],
    gold: Sequence[str],
) -> List[dict]:
    """``hops`` is a list of ``(hop_name, text)`` pairs."""
    rows = []
    for name, text in hops:
        hits = extract_entities(text, gold)
        kept = [h.mention for h in hits if h.present]
        lost = [h.mention for h in hits if not h.present]
        rows.append(
            {
                "hop": name,
                "kept": kept,
                "lost": lost,
                "retention": (len(kept) / len(hits)) if hits else 1.0,
            }
        )
    return rows


def unique_preserve(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        key = fold(item)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out
