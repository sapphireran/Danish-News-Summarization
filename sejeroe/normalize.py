"""Shared Unicode folding for slot, quote, and connective matching."""

from __future__ import annotations

import re
import unicodedata

_DASHES = dict.fromkeys(map(ord, "–—−‐‑"), "-")
_QUOTES = dict.fromkeys(map(ord, "“”„‟«»"), '"')
_SPACES = re.compile(r"\s+")


def fold(text: str) -> str:
    """Lowercase, flatten dashes/quotes, and collapse whitespace."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.translate(_DASHES).translate(_QUOTES)
    normalized = normalized.replace("\u00a0", " ")
    return _SPACES.sub(" ", normalized).strip().lower()


def contains_phrase(haystack: str, needle: str) -> bool:
    hay = fold(haystack)
    needle_fold = fold(needle)
    if not needle_fold:
        return False
    return needle_fold in hay
