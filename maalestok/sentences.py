"""Danish-aware sentence splitter for almanac prose.

The 2023 scripts call ``nltk.sent_tokenize`` (English Punkt) on both Danish
source and English pivots. Punkt treats ``kl.``, ``kr.``, ``t.eks.``, and
``12. juni`` poorly. This splitter is the control: same articles, fewer false
cuts, so packing windows are not dominated by abbreviation scars.
"""

from __future__ import annotations

import re

# Periods that do not end a sentence when they appear as their own token.
_ABBREV = {
    "t.eks.",
    "bl.a.",
    "m.fl.",
    "m.m.",
    "osv.",
    "ca.",
    "inkl.",
    "ekskl.",
    "kl.",
    "dr.",
    "hr.",
    "fru.",
    "fr.",
    "prof.",
    "nr.",
    "mdl.",
    "mio.",
    "mia.",
    "jan.",
    "feb.",
    "apr.",
    "jun.",
    "jul.",
    "aug.",
    "sep.",
    "okt.",
    "nov.",
    "dec.",
    "man.",
    "tirs.",
    "ons.",
    "tors.",
    "fre.",
    "lør.",
    "søn.",
    "skt.",
    "dvs.",
    "ift.",
    "pr.",
    "pct.",
}

# Month names that follow an ordinal day: ``12. juni``.
_MONTHS = (
    "januar",
    "februar",
    "marts",
    "april",
    "maj",
    "juni",
    "juli",
    "august",
    "september",
    "oktober",
    "november",
    "december",
)

_ORDINAL_FOLLOW = (
    "klasse",
    "søndag",
    "mandag",
    "tirsdag",
    "onsdag",
    "torsdag",
    "fredag",
    "lørdag",
    "plads",
    "etage",
    "sal",
    "række",
)

_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÆØÅ0-9\"“])")


def split_sentences(text: str) -> list[str]:
    """Split *text* into sentences without cutting Danish abbreviations."""
    text = re.sub(r"[ \t]+", " ", text.replace("\r\n", "\n")).strip()
    if not text:
        return []
    # Protect dotted abbreviations and ordinal dates by swapping the period.
    protected = _protect(text)
    parts = _SPLIT.split(protected)
    sentences = [_unprotect(part).strip() for part in parts if part.strip()]
    return sentences


def _protect(text: str) -> str:
    out = text
    # Times: kl. 8.15 / 06.00 — protect both the abbrev and the clock dots.
    out = re.sub(
        r"\bkl\.\s*(\d{1,2})[.:](\d{2})",
        lambda m: f"kl¤ {m.group(1)}¤{m.group(2)}",
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(
        r"\b(\d{1,2})[.:](\d{2})\s*[–-]\s*(\d{1,2})[.:](\d{2})",
        lambda m: f"{m.group(1)}¤{m.group(2)}–{m.group(3)}¤{m.group(4)}",
        out,
    )
    for abbr in sorted(_ABBREV, key=len, reverse=True):
        needle = abbr
        out = re.sub(re.escape(needle), needle.replace(".", "¤"), out, flags=re.IGNORECASE)
    # ``18 kr. Bussen…`` is a real sentence end. ``18 kr. pr. ton`` is not.
    out = re.sub(r"\bkr\.(?!\s+[A-ZÆØÅ])", "kr¤", out, flags=re.IGNORECASE)
    # Ordinal day + month: 12. juni / 14. januar
    months = "|".join(_MONTHS)
    out = re.sub(
        rf"\b(\d{{1,2}})\.\s+({months})\b",
        lambda m: f"{m.group(1)}¤ {m.group(2)}",
        out,
        flags=re.IGNORECASE,
    )
    # Ordinal labels: 1. klasse, 3. søndag
    follow = "|".join(_ORDINAL_FOLLOW)
    out = re.sub(
        rf"\b(\d{{1,2}})\.\s+({follow})\b",
        lambda m: f"{m.group(1)}¤ {m.group(2)}",
        out,
        flags=re.IGNORECASE,
    )
    # Weekday abbreviations already handled via _ABBREV (man.–tors.)
    # Initials: A. B. Holm — protect single-letter capitals.
    out = re.sub(r"\b([A-ZÆØÅ])\.(?=\s)", r"\1¤", out)
    return out


def _unprotect(text: str) -> str:
    return text.replace("¤", ".")
