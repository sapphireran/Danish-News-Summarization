"""Sentence splitting and length-aware window packing.

The original course scripts (`translate.py`, `summary.py`, `translate_back.py`)
all reimplement the same idea: OPUS-MT and the English T5 news model were
trained with a 512-token context, so a Danish news article has to be carved
into windows that fit. Those scripts mix *character* counts with a *token*
budget in a few places. This module keeps both units explicit.

Danish news text is abbreviation-heavy (`f.eks.`, `bl.a.`, `mio. kr.`)
and date-heavy (`den 12. oktober`). A naive split on every period produces
broken sentences and therefore broken translation windows. The splitter
below protects a small, documented set of Danish abbreviations, decimal /
thousand-separator points, and ordinal periods before a lowercase word.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Iterable, Literal, Sequence

Unit = Literal["chars", "words", "tokens"]
TokenizeFn = Callable[[str], Sequence[str]]

# Period-containing abbreviations seen in Danish news copy. Stored without the
# final period so `f.eks.` and `f.eks` both match. Keep this list conservative:
# over-protecting (`A.` as an initial) is less harmful than under-protecting
# (`f.eks.` split into a one-word "sentence").
DANISH_ABBREVIATIONS = frozenset(
    {
        "ang",
        "apr",
        "aug",
        "bl.a",
        "ca",
        "dec",
        "dr",
        "dvs",
        "etc",
        "f.eks",
        "feb",
        "fhv",
        "fig",
        "fru",
        "hhv",
        "hr",
        "iflg",
        "jan",
        "jf",
        "jfr",
        "jul",
        "jun",
        "kl",
        "kr",
        "m.fl",
        "m.v",
        "mar",
        "mia",
        "mio",
        "nov",
        "nr",
        "okt",
        "osv",
        "pct",
        "pga",
        "prof",
        "sep",
        "t.d",
    }
)

_SENTENCE_END = re.compile(r"([.!?])([\"»”’']?)(\s+|$)")
_DECIMAL = re.compile(r"(?<=\d)\.(?=\d)")
# Danish ordinals in dates: "den 12. oktober". Only protect when the next
# word is lowercase; a capital after `12.` is treated as a real sentence.
_ORDINAL = re.compile(r"(?<=\d)\.(?=\s+[a-zæøå])")
_ELLIPSIS = re.compile(r"\.{2,}")
_WHITESPACE = re.compile(r"\s+")
_WORD = re.compile(r"[A-Za-zÆØÅæøå0-9]+(?:-[A-Za-zÆØÅæøå0-9]+)*|[.,;:!?]")


@dataclass(frozen=True)
class Window:
    """One model-sized slice of an article."""

    texts: tuple[str, ...]
    unit_count: int
    unit: Unit

    @property
    def text(self) -> str:
        return " ".join(self.texts)


def default_word_tokenize(text: str) -> list[str]:
    """Lightweight tokenizer that keeps Danish letters and hyphenated compounds."""
    return _WORD.findall(text)


def measure(text: str, unit: Unit, tokenize_fn: TokenizeFn | None = None) -> int:
    """Count a string in the unit the caller asked for."""
    if unit == "chars":
        return len(text)
    tokenizer = tokenize_fn or default_word_tokenize
    return len(tokenizer(text))


def split_sentences(text: str) -> list[str]:
    """Split Danish (or English) copy into sentences.

    Protection order:
    1. Collapse runs of periods so ellipses do not become empty sentences.
    2. Replace decimal points / thousand separators (`12.5`, `1.200`).
    3. Replace Danish ordinal periods before a lowercase word (`12. oktober`).
    4. Replace abbreviation periods with the same placeholder.
    5. Cut on remaining `.!?` when followed by whitespace.
    6. Restore placeholders.
    """
    if not text or not text.strip():
        return []

    prepared = _ELLIPSIS.sub("…", text.strip())
    prepared = _DECIMAL.sub("∯", prepared)
    prepared = _ORDINAL.sub("∯", prepared)
    prepared = _protect_abbreviations(prepared)

    sentences: list[str] = []
    start = 0
    for match in _SENTENCE_END.finditer(prepared):
        end = match.end()
        sentence = prepared[start:end].replace("∯", ".").replace("…", "...")
        sentence = _WHITESPACE.sub(" ", sentence).strip()
        if sentence:
            sentences.append(sentence)
        start = end
    tail = prepared[start:].replace("∯", ".").replace("…", "...")
    tail = _WHITESPACE.sub(" ", tail).strip()
    if tail:
        sentences.append(tail)
    return sentences


def split_long_sentence(
    sentence: str,
    max_units: int,
    unit: Unit = "words",
    tokenize_fn: TokenizeFn | None = None,
    prefer_breaks: Sequence[str] = (",", ";", ":"),
) -> list[str]:
    """Split one overlong sentence on punctuation, then on words.

    Mirrors `split_long_sentence` in `translate.py` / `summary.py`, but the
    unit is explicit. The course scripts compared `len(word) + 1` (characters)
    against a 512-token budget; pass `unit="chars"` to reproduce that mix.
    """
    if max_units <= 0:
        raise ValueError("max_units must be positive")

    tokenizer = tokenize_fn or default_word_tokenize
    if measure(sentence, unit, tokenizer) <= max_units:
        return [sentence]

    words = tokenizer(sentence)
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    def flush() -> None:
        nonlocal current, current_length
        if current:
            chunks.append(_join_tokens(current))
            current = []
            current_length = 0

    for word in words:
        addition = _token_cost(word, unit)
        tentative = current_length + addition
        at_break = word in prefer_breaks and tentative < max_units
        if current and tentative > max_units:
            flush()
            current = [word]
            current_length = addition
            continue
        current.append(word)
        current_length = tentative if current_length else addition
        if at_break:
            flush()

    flush()
    return chunks or [sentence]


def pack_windows(
    sentences: Iterable[str],
    max_units: int,
    unit: Unit = "words",
    tokenize_fn: TokenizeFn | None = None,
) -> list[Window]:
    """Greedy-pack sentences into windows that stay under `max_units`."""
    if max_units <= 0:
        raise ValueError("max_units must be positive")

    tokenizer = tokenize_fn or default_word_tokenize
    windows: list[Window] = []
    current: list[str] = []
    current_length = 0

    def close() -> None:
        nonlocal current, current_length
        if current:
            windows.append(Window(tuple(current), current_length, unit))
            current = []
            current_length = 0

    for sentence in sentences:
        pieces = split_long_sentence(sentence, max_units, unit, tokenizer)
        for piece in pieces:
            length = measure(piece, unit, tokenizer)
            # A single piece can still exceed the budget if the tokenizer
            # disagrees with the splitter; keep it in its own window rather
            # than dropping text.
            if current and current_length + length > max_units:
                close()
            current.append(piece)
            current_length += length
    close()
    return windows


def split_into_windows(
    article: str,
    max_units: int,
    unit: Unit = "words",
    tokenize_fn: TokenizeFn | None = None,
) -> list[Window]:
    """Split an article into sentences, then pack those sentences into windows."""
    return pack_windows(split_sentences(article), max_units, unit, tokenize_fn)


def _protect_abbreviations(text: str) -> str:
    """Replace the final period of a known abbreviation with a placeholder."""

    def replacer(match: re.Match[str]) -> str:
        token = match.group(0)
        stem = token[:-1]
        if stem.lower() in DANISH_ABBREVIATIONS:
            return stem + "∯"
        return token

    # Greedy `[\w.]+` consumes inner periods so `f.eks.` is one token, not `f.`
    return re.sub(r"\b[\w.]+\.", replacer, text)


def _token_cost(token: str, unit: Unit) -> int:
    if unit == "chars":
        return len(token) + 1
    return 1


def _join_tokens(tokens: Sequence[str]) -> str:
    """Join tokens without a space before punctuation."""
    out: list[str] = []
    for token in tokens:
        if out and re.fullmatch(r"[.,;:!?]", token):
            out[-1] = out[-1] + token
        elif out:
            out.append(" " + token)
        else:
            out.append(token)
    return "".join(out)
