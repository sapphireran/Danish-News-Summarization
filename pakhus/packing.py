"""Window packers: 2023 control flow, plus a consistent-unit baseline.

See docs/02-packing-algorithm.md for the prose reconstruction. Function
names map to course files:

- `pack_course_translate` → `translate.py`
- `pack_course_summary` → `summary.py`
- `pack_course_back` → `translate_back.py` (no long saw, budget 512)
- `pack_consistent` → personal baseline (one unit, no empty panes)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence

from pakhus.sentences import split_danish, split_naive
from pakhus.tokenize import (
    approx_encode_len,
    char_word_len,
    detokenize_course,
    detokenize_tight,
    word_tokenize,
)

LengthFn = Callable[[str], int]


@dataclass(frozen=True)
class Pane:
    """One packed window (a crate on the dock)."""

    pane_id: int
    sentences: tuple[str, ...]
    unit_sum: int
    budget: int
    empty: bool = False
    over_budget: bool = False
    sawed: bool = False
    notes: tuple[str, ...] = ()

    @property
    def text(self) -> str:
        return " ".join(self.sentences).strip()

    @property
    def n_sentences(self) -> int:
        return len(self.sentences)

    @property
    def fill_ratio(self) -> float:
        if self.budget <= 0:
            return 0.0
        return self.unit_sum / self.budget

    @property
    def leftover(self) -> int:
        return max(0, self.budget - self.unit_sum)

    def as_dict(self) -> dict[str, object]:
        return {
            "pane_id": self.pane_id,
            "n_sentences": self.n_sentences,
            "approx_units": self.unit_sum,
            "budget": self.budget,
            "fill_ratio": round(self.fill_ratio, 4),
            "leftover": self.leftover,
            "empty": self.empty,
            "over_budget": self.over_budget,
            "sawed": self.sawed,
            "text": self.text,
        }


@dataclass
class PackResult:
    packer: str
    budget: int
    panes: list[Pane] = field(default_factory=list)
    source_sentences: tuple[str, ...] = ()
    saw_fragments: int = 0

    @property
    def n_panes(self) -> int:
        return len(self.panes)

    @property
    def n_empty(self) -> int:
        return sum(1 for p in self.panes if p.empty)

    @property
    def n_over_budget(self) -> int:
        return sum(1 for p in self.panes if p.over_budget)

    @property
    def last_fill(self) -> float:
        if not self.panes:
            return 0.0
        return self.panes[-1].fill_ratio


def split_long_sentence_course(sentence: str, max_length: int) -> list[str]:
    """Character-budget saw from `translate.py` / `summary.py`."""
    words = word_tokenize(sentence)
    current_chunk: list[str] = []
    chunks: list[str] = []
    current_length = 0
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if word in [",", ";", ":"] and current_length < max_length:
            chunks.append(detokenize_course(current_chunk))
            current_chunk = []
            current_length = 0
        elif current_length >= max_length:
            last_word = current_chunk.pop()
            # Course code appends even when the chunk is empty: a single
            # token longer than the character budget yields a blank crate
            # plus the oversized token. Keep that scar.
            chunks.append(detokenize_course(current_chunk))
            current_chunk = [last_word]
            current_length = len(last_word) + 1
    if current_chunk:
        chunks.append(detokenize_course(current_chunk))
    return chunks or [sentence]


def _units_with_optional_saw(
    sentences: Sequence[str],
    *,
    budget: int,
    encode: LengthFn,
    saw: bool,
) -> list[tuple[str, int, bool]]:
    out: list[tuple[str, int, bool]] = []
    for sentence in sentences:
        encoded = encode(sentence)
        if saw and encoded > budget:
            for chunk in split_long_sentence_course(sentence, budget):
                out.append((chunk, encode(chunk), True))
        else:
            out.append((sentence, encoded, False))
    return out


def _accumulate(
    units: Sequence[tuple[str, int, bool]],
    *,
    budget: int,
    drop_empty: bool,
) -> list[Pane]:
    """Course accumulator, including the empty-list scar when drop_empty is False."""
    panes: list[Pane] = []
    current_list: list[str] = []
    current_length = 0
    current_sawed = False

    def flush(empty_ok: bool) -> None:
        nonlocal current_list, current_length, current_sawed
        if not current_list and not empty_ok:
            return
        empty = len(current_list) == 0
        over = current_length > budget
        panes.append(
            Pane(
                pane_id=len(panes),
                sentences=tuple(current_list),
                unit_sum=current_length,
                budget=budget,
                empty=empty,
                over_budget=over,
                sawed=current_sawed,
                notes=tuple(
                    n
                    for n in (
                        "empty-list-scar" if empty else "",
                        "over-budget-singleton" if over else "",
                    )
                    if n
                ),
            )
        )
        current_list = []
        current_length = 0
        current_sawed = False

    for sentence, length, sawed in units:
        if current_length + length > budget:
            flush(empty_ok=not drop_empty)
            current_list = [sentence]
            current_length = length
            current_sawed = sawed
        else:
            current_list.append(sentence)
            current_length += length
            current_sawed = current_sawed or sawed
    if current_list or not drop_empty:
        # Final flush: never emit a trailing empty pane.
        if current_list:
            flush(empty_ok=False)
    return panes


def _pack(
    text: str,
    *,
    packer: str,
    budget: int,
    splitter: Callable[[str], list[str]],
    encode: LengthFn,
    saw: bool,
    drop_empty: bool,
) -> PackResult:
    sentences = splitter(text)
    units = _units_with_optional_saw(sentences, budget=budget, encode=encode, saw=saw)
    panes = _accumulate(units, budget=budget, drop_empty=drop_empty)
    return PackResult(
        packer=packer,
        budget=budget,
        panes=panes,
        source_sentences=tuple(sentences),
        saw_fragments=sum(1 for _, _, sawed in units if sawed),
    )


def pack_course_translate(text: str, budget: int = 460) -> PackResult:
    """`translate.py`: Danish splitter stand-in, character saw, budget 460."""
    return _pack(
        text,
        packer="course_translate",
        budget=budget,
        splitter=split_danish,
        encode=approx_encode_len,
        saw=True,
        drop_empty=False,
    )


def pack_course_summary(text: str, budget: int = 512) -> PackResult:
    """`summary.py`: same saw, T5-sized budget."""
    return _pack(
        text,
        packer="course_summary",
        budget=budget,
        splitter=split_naive,
        encode=approx_encode_len,
        saw=True,
        drop_empty=False,
    )


def pack_course_back(text: str, budget: int = 512) -> PackResult:
    """`translate_back.py`: no long saw, budget 512 (not the unused 460)."""
    return _pack(
        text,
        packer="course_back",
        budget=budget,
        splitter=split_naive,
        encode=approx_encode_len,
        saw=False,
        drop_empty=False,
    )


def pack_consistent(
    text: str,
    budget: int = 460,
    *,
    splitter: Callable[[str], list[str]] | None = None,
) -> PackResult:
    """Single unit, Danish splits, drop empty panes, resplit leftover overs."""
    split = splitter or split_danish
    encode = approx_encode_len
    sentences = split(text)
    units: list[tuple[str, int, bool]] = []
    for sentence in sentences:
        encoded = encode(sentence)
        if encoded > budget:
            # Split on comma-like punctuation using the SAME unit, then
            # fall back to token chunks if a fragment is still over.
            pieces = _split_on_clauses(sentence, budget, encode)
            for piece in pieces:
                units.append((piece, encode(piece), True))
        else:
            units.append((sentence, encoded, False))
    panes = _accumulate(units, budget=budget, drop_empty=True)
    # Guard: a singleton over-budget pane gets force-chunked by words.
    repaired: list[Pane] = []
    for pane in panes:
        if pane.over_budget and pane.n_sentences == 1:
            repaired.extend(_force_chunk_pane(pane, budget, encode))
        else:
            repaired.append(pane)
    repaired = [
        Pane(
            pane_id=i,
            sentences=p.sentences,
            unit_sum=p.unit_sum,
            budget=p.budget,
            empty=p.empty,
            over_budget=p.over_budget,
            sawed=p.sawed,
            notes=p.notes,
        )
        for i, p in enumerate(repaired)
    ]
    return PackResult(
        packer="consistent",
        budget=budget,
        panes=repaired,
        source_sentences=tuple(sentences),
        saw_fragments=sum(1 for _, _, sawed in units if sawed),
    )


def _split_on_clauses(sentence: str, budget: int, encode: LengthFn) -> list[str]:
    tokens = word_tokenize(sentence)
    chunks: list[str] = []
    current: list[str] = []
    for tok in tokens:
        trial = current + [tok]
        if current and encode(detokenize_tight(trial)) > budget and tok in {",", ";", ":"}:
            current.append(tok)
            chunks.append(detokenize_tight(current))
            current = []
            continue
        if encode(detokenize_tight(trial)) > budget and current:
            chunks.append(detokenize_tight(current))
            current = [tok]
        else:
            current.append(tok)
    if current:
        chunks.append(detokenize_tight(current))
    return chunks or [sentence]


def _force_chunk_pane(pane: Pane, budget: int, encode: LengthFn) -> list[Pane]:
    tokens = word_tokenize(pane.text)
    chunks: list[str] = []
    current: list[str] = []
    for tok in tokens:
        trial = current + [tok]
        if current and encode(detokenize_tight(trial)) > budget:
            chunks.append(detokenize_tight(current))
            current = [tok]
        else:
            current.append(tok)
    if current:
        chunks.append(detokenize_tight(current))
    out: list[Pane] = []
    for chunk in chunks:
        length = encode(chunk)
        out.append(
            Pane(
                pane_id=0,  # renumbered by caller
                sentences=(chunk,),
                unit_sum=length,
                budget=budget,
                empty=False,
                over_budget=length > budget,
                sawed=True,
                notes=("force-chunked",),
            )
        )
    # pane_id rewrite happens in pack_consistent
    return [
        Pane(
            pane_id=i,
            sentences=p.sentences,
            unit_sum=p.unit_sum,
            budget=p.budget,
            empty=p.empty,
            over_budget=p.over_budget,
            sawed=p.sawed,
            notes=p.notes,
        )
        for i, p in enumerate(out)
    ]


PACKERS = {
    "course_translate": pack_course_translate,
    "course_summary": pack_course_summary,
    "course_back": pack_course_back,
    "consistent": pack_consistent,
}


def pack_named(name: str, text: str) -> PackResult:
    if name not in PACKERS:
        known = ", ".join(sorted(PACKERS))
        raise KeyError(f"unknown packer {name!r}; choose from {known}")
    return PACKERS[name](text)


def pane_table(result: PackResult) -> list[dict[str, object]]:
    return [p.as_dict() for p in result.panes]


def fill_bar(pane: Pane, width: int = 40) -> str:
    filled = int(round(min(1.0, pane.fill_ratio) * width))
    filled = min(width, max(0, filled))
    return "[" + "#" * filled + "." * (width - filled) + "]"


def ascii_atlas(result: PackResult, article_id: str = "") -> str:
    lines = [
        f"packer={result.packer}  budget={result.budget}  "
        f"panes={result.n_panes}  saw_fragments={result.saw_fragments}  "
        f"empty={result.n_empty}  over_budget={result.n_over_budget}"
        + (f"  article={article_id}" if article_id else "")
    ]
    if not result.panes:
        lines.append("(no panes)")
        return "\n".join(lines)
    for pane in result.panes:
        flag = ""
        if pane.empty:
            flag = "  EMPTY"
        elif pane.over_budget:
            flag = "  OVER"
        elif pane.fill_ratio < 0.4:
            flag = "  UNDERFILLED"
        lines.append(
            f"pane {pane.pane_id:02d}  {fill_bar(pane)}  "
            f"{pane.unit_sum:4d}/{pane.budget}  leftover {pane.leftover:4d}  "
            f"sents {pane.n_sentences:2d}{flag}"
        )
    return "\n".join(lines)


def character_vs_token_demo(sentence: str, budget: int = 460) -> dict[str, int]:
    """Show why the course saw over-fragments long Danish sentences."""
    tokens = word_tokenize(sentence)
    return {
        "char_word_len": char_word_len(tokens),
        "approx_encode_len": approx_encode_len(sentence),
        "course_saw_chunks": len(split_long_sentence_course(sentence, budget)),
        "budget": budget,
    }
