"""Danish-aware tokenization and sentence splitting (stdlib only).

The 2023 scripts called ``nltk.sent_tokenize`` / ``nltk.word_tokenize`` after
``nltk.download('punkt')``. Punkt is English-tuned: it is decent on Danish
news prose but trips on ``kr.``, ``bl.a.``, ``kl.``, and decimal commas.
This module is the workbook stand-in so examples stay download-free.
"""

from __future__ import annotations

import re
from unicodedata import normalize as u_normalize

# Abbreviations that should not end a sentence when followed by a capital.
_ABBREV = {
    "hr",
    "fr",
    "frk",
    "dr",
    "ca",
    "bl.a",
    "f.eks",
    "osv",
    "kr",
    "nr",
    "kl",
    "jf",
    "mio",
    "mia",
    "pct",
    "tlf",
    "adr",
    "d",
    "s",
    "kap",
    "fig",
    "eng",
    "da",
    "km",
    "kg",
}

# Titles: never treat the following capital as a new sentence.
_TITLES = {"dr", "hr", "fr", "frk"}

# Tokens that look like initials: "S." in "S. Brix" — keep attached.
_INITIAL = re.compile(r"^[A-ZÆØÅ]\.$")

# Word / number / time / leftover punctuation.
_TOKEN = re.compile(
    r"[0-9]{1,2}:[0-9]{2}"
    r"|[0-9]+(?:[.,][0-9]+)*"
    r"|[\wÆØÅæøå]+(?:-[\wÆØÅæøå]+)*"
    r"|[^\w\s]",
    re.UNICODE,
)

_WORD_ONLY = re.compile(r"[\wÆØÅæøå]+(?:-[\wÆØÅæøå]+)*", re.UNICODE)

# Sentence end: . ! ? … optionally followed by extra punctuation / quotes.
_END = re.compile(r'([.!?…]+)([»"\')\]]*)(\s+|$)')


def normalize(text: str) -> str:
    """Casefold, NFC-normalize, collapse whitespace, strip most punctuation."""
    text = u_normalize("NFC", text or "")
    text = text.replace("\u00a0", " ")
    text = text.casefold()
    text = re.sub(r"[«»\"'()\[\]{};!?…/\\]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def word_tokenize(text: str) -> list[str]:
    """NLTK-like tokenization: words, numbers, times, and lone punctuation."""
    text = u_normalize("NFC", text or "")
    return _TOKEN.findall(text)


def content_tokens(text: str) -> list[str]:
    """Alphabetic / numeric tokens only (no lone punctuation)."""
    return [tok for tok in word_tokenize(text) if _WORD_ONLY.fullmatch(tok) or ":" in tok]


def split_sentences(text: str) -> list[str]:
    """Split on .!? while protecting Danish abbreviations and decimals.

    ``25 kr. Hallen åbner`` still splits (abbreviation + new sentence).
    ``Dr. Holm målte 3,5 km.`` stays one sentence until the final period.
    """
    text = u_normalize("NFC", (text or "").strip())
    if not text:
        return []

    sentences: list[str] = []
    start = 0
    for match in _END.finditer(text):
        end_punct = match.group(1)
        # Decimal / thousand-separator: digit . digit
        prev = text[match.start() - 1] if match.start() else ""
        nxt_nonspace = _next_nonspace(text, match.end())
        if prev.isdigit() and nxt_nonspace[:1].isdigit() and end_punct == ".":
            continue
        # Abbreviation: look at the token before the period.
        token_before = _token_before(text, match.start())
        bare = token_before.rstrip(".").casefold()
        if bare in _ABBREV:
            # Titles stick to the following name. Other abbreviations split
            # only when a real new sentence starts with a capital.
            if bare in _TITLES or not _looks_like_new_sentence(text, match.end()):
                continue
        if _INITIAL.fullmatch(token_before) and nxt_nonspace[:1].isupper():
            continue
        end = match.end()
        piece = text[start:end].strip()
        if piece:
            sentences.append(piece)
        start = match.end()
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def _next_nonspace(text: str, index: int) -> str:
    while index < len(text) and text[index].isspace():
        index += 1
    return text[index : index + 12]


def _token_before(text: str, period_index: int) -> str:
    i = period_index - 1
    while i >= 0 and text[i].isspace():
        i -= 1
    end = i + 1
    while i >= 0 and not text[i].isspace():
        i -= 1
    return text[i + 1 : end]


def _looks_like_new_sentence(text: str, after_end: int) -> bool:
    nxt = _next_nonspace(text, after_end)
    if not nxt:
        return False
    # A following capitalised function word is a new sentence; a lowercase
    # continuation after kr./ca. is not.
    if nxt[0].islower():
        return False
    # ``kr. Hallen`` — Hallen is capitalised (Danish definite noun as name).
    # Treat any capital after an abbreviation as a new sentence *unless* it
    # looks like a middle initial (single letter).
    if re.match(r"^[A-ZÆØÅ]\.(\s|$)", nxt):
        return False
    return nxt[0].isupper()


def lead_n(text: str, n: int = 2) -> str:
    """First *n* sentences, joined with a single space."""
    sents = split_sentences(text)
    return " ".join(sents[:n])
