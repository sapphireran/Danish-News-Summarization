"""Danish-aware sentence cuts versus a naive regex split.

The 2023 scripts call `nltk.sent_tokenize` after `nltk.download('punkt')`.
Default punkt is English-trained and over-splits Danish clocks, ordinal
dates, and `mio. kr.`. This module does not reimplement punkt. It offers:

- `split_naive`: cut on `[.!?]` plus whitespace (the failure mode).
- `split_danish`: protect a closed list of news abbreviations and ordinal
  dates so packing experiments are not dominated by false boundaries.
"""

from __future__ import annotations

import re

DANISH_MONTHS = (
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
    "jan",
    "feb",
    "mar",
    "apr",
    "jun",
    "jul",
    "aug",
    "sep",
    "okt",
    "nov",
    "dec",
)

# Tokens that may appear immediately before a period without ending a sentence.
# Stored lowercase, without the trailing period.
ABBREV_TOKENS = {
    "hr",
    "fr",
    "frk",
    "dr",
    "prof",
    "mr",
    "ms",
    "nr",
    "kl",
    "ca",
    "pr",
    "pt",
    "kr",
    "mio",
    "mia",
    "pct",
    "stk",
    "osv",
    "dvs",
    "ifm",
    "ift",
    "hhv",
    "evt",
    "inkl",
    "ekskl",
    "jf",
    "jfr",
    "pga",
    "pvsa",
    "skt",
    "st",
    "tlf",
    "att",
    *DANISH_MONTHS,
}

# Multi-period abbreviations protected as placeholders before the scan.
MULTI_ABBREV = (
    "bl.a.",
    "f.eks.",
    "m.fl.",
    "m.v.",
    "m.m.",
    "d.v.s.",
    "t.o.m.",
    "f.o.m.",
    "o.l.",
    "m.m.",
)

_MULTI_PATTERN = re.compile(
    "|".join(re.escape(a) for a in sorted(set(MULTI_ABBREV), key=len, reverse=True)),
    flags=re.IGNORECASE,
)

_TERMINATOR = {".", "?", "!"}


def split_naive(text: str) -> list[str]:
    """Split on `.`, `?`, or `!` followed by whitespace. Keeps the mark."""
    if not text or not text.strip():
        return []
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _protect_multi(text: str) -> tuple[str, dict[str, str]]:
    table: dict[str, str] = {}

    def repl(match: re.Match[str]) -> str:
        key = f"⟦ABBR{len(table)}⟧"
        table[key] = match.group(0)
        return key

    return _MULTI_PATTERN.sub(repl, text), table


def _restore(text: str, table: dict[str, str]) -> str:
    for key, value in table.items():
        text = text.replace(key, value)
    return text


def _last_word_lower(buffer: str) -> str:
    tokens = re.findall(r"\w+", buffer, flags=re.UNICODE)
    if not tokens:
        return ""
    return tokens[-1].lower()


def _next_significant(text: str, index: int) -> str:
    j = index
    while j < len(text) and text[j].isspace():
        j += 1
    if j >= len(text):
        return ""
    return text[j]


def _next_word(text: str, index: int) -> str:
    j = index
    while j < len(text) and text[j].isspace():
        j += 1
    chars: list[str] = []
    while j < len(text) and (text[j].isalnum() or text[j] in ".-"):
        chars.append(text[j])
        j += 1
    return "".join(chars)


def _is_ordinal_date(buffer: str, text: str, period_index: int) -> bool:
    """True for `12. oktober` / `12. okt.` — the period is an ordinal marker."""
    prefix = buffer.rstrip()
    if not re.search(r"\d+$", prefix):
        return False
    nxt = _next_word(text, period_index + 1).lower().rstrip(".")
    return nxt in DANISH_MONTHS


def _is_clock_tail(text: str, period_index: int) -> bool:
    """True for `19.30` after `kl.` was already consumed as abbreviation.

    Also used when the period sits between hour and minutes without `kl.`
    immediately before it (`mødet begynder 19.30 i pakhuset`).
    """
    nxt = _next_significant(text, period_index + 1)
    return nxt.isdigit()


def _looks_like_new_sentence(text: str, period_index: int) -> bool:
    nxt = _next_significant(text, period_index + 1)
    if nxt == "":
        return True
    if nxt in "\"»«“”'(":
        return True
    return nxt.isupper()


def split_danish(text: str) -> list[str]:
    """Split Danish news prose without cutting clocks, ordinals, or `mio. kr.`."""
    if not text or not text.strip():
        return []
    protected, table = _protect_multi(text.strip())
    sentences: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(protected)
    while i < n:
        ch = protected[i]
        buf.append(ch)
        if ch in _TERMINATOR:
            body = "".join(buf[:-1])
            last = _last_word_lower(body)
            if ch == "." and last in ABBREV_TOKENS:
                i += 1
                continue
            if ch == "." and _is_ordinal_date(body, protected, i):
                i += 1
                continue
            if ch == "." and _is_clock_tail(protected, i):
                i += 1
                continue
            if _looks_like_new_sentence(protected, i):
                # Swallow trailing quotes that belong to this sentence.
                j = i + 1
                while j < n and protected[j] in "\"»«“”'":
                    buf.append(protected[j])
                    j += 1
                sent = _restore("".join(buf).strip(), table)
                if sent:
                    sentences.append(sent)
                buf = []
                i = j
                while i < n and protected[i].isspace():
                    i += 1
                continue
        i += 1
    tail = _restore("".join(buf).strip(), table)
    if tail:
        sentences.append(tail)
    return sentences


def count_false_boundaries(text: str) -> dict[str, int]:
    """How many extra cuts the naive splitter makes relative to Danish split."""
    naive = split_naive(text)
    danish = split_danish(text)
    return {
        "naive_sentences": len(naive),
        "danish_sentences": len(danish),
        "extra_naive_cuts": max(0, len(naive) - len(danish)),
    }
