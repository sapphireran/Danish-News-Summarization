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


def mention_in_text(mention: str, text: str) -> bool:
    if not mention or not text:
        return False
    folded_mention = fold(mention)
    folded_text = fold(text)
    if not folded_mention:
        return False
    if folded_mention in folded_text:
        return True
    tokens = [t for t in lowercase_words(mention) if not t.isdigit() or True]
    if not tokens:
        return False
    text_tokens = set(lowercase_words(text))
    # Require all alphabetic tokens; numbers may use different punctuation.
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
