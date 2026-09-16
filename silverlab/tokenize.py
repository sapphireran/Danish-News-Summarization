"""Whitespace-and-punctuation tokenizer that keeps Danish letters.

The 2023 scripts delegated tokenization to Hugging Face and NLTK. This module
is the opposite: a tiny, testable fold used by ROUGE, TextRank, and the
annotation rubric so the lab can run without downloading punkt or a tokenizer.
"""

from __future__ import annotations

import re
from typing import Iterable, List

# Keep digits and the Danish vowel letters. Apostrophes stay inside a token so
# "l'oreal"-style fragments do not explode; they barely appear in this corpus.
WORD_RE = re.compile(
    r"[0-9A-Za-zÆØÅæøåÄÖÜäöüÉé]+(?:['’][0-9A-Za-zÆØÅæøåÄÖÜäöüÉé]+)?",
    re.UNICODE,
)

# A short closed-class list for content-word baselines. Not a linguist's
# lexicon — just enough to stop TextRank from ranking "og" and "det".
DANISH_STOPWORDS = frozenset(
    {
        "af",
        "aldrig",
        "alle",
        "at",
        "blev",
        "bliver",
        "da",
        "de",
        "dem",
        "den",
        "denne",
        "der",
        "deres",
        "det",
        "dette",
        "dig",
        "din",
        "disse",
        "du",
        "efter",
        "eller",
        "en",
        "er",
        "et",
        "for",
        "fra",
        "han",
        "hans",
        "har",
        "have",
        "hende",
        "hendes",
        "hun",
        "hvad",
        "hvis",
        "hvor",
        "i",
        "ikke",
        "ind",
        "jeg",
        "jer",
        "jeres",
        "kan",
        "kom",
        "kommer",
        "kun",
        "man",
        "med",
        "men",
        "mere",
        "mig",
        "min",
        "når",
        "og",
        "også",
        "om",
        "op",
        "os",
        "over",
        "på",
        "sig",
        "sin",
        "sine",
        "sit",
        "skal",
        "som",
        "så",
        "til",
        "ud",
        "under",
        "var",
        "ved",
        "vi",
        "vil",
        "vores",
        "være",
    }
)


def fold(text: str) -> str:
    """Case-fold without stripping æ/ø/å. Danish identity lives in those letters."""
    return (text or "").casefold()


def tokenize(text: str) -> List[str]:
    """Return folded word tokens. Empty or None-like input yields []."""
    if not text:
        return []
    return WORD_RE.findall(fold(text))


def content_tokens(text: str) -> List[str]:
    """Tokens that are not stopwords and not pure digits."""
    return [tok for tok in tokenize(text) if tok not in DANISH_STOPWORDS and not tok.isdigit()]


def ngrams(tokens: Iterable[str], n: int) -> List[tuple[str, ...]]:
    seq = list(tokens)
    if n < 1 or len(seq) < n:
        return []
    return [tuple(seq[i : i + n]) for i in range(len(seq) - n + 1)]
