"""Sentence packing windows, mirroring the 2023 ``split_into_sentences`` loops.

``translate.py`` and ``summary.py`` greedily fill a list until the next
sentence would exceed ``int(max_length * 0.9)``. Overflow sentences are first
cut on commas using a word/character hybrid. ``translate_back.py`` uses the
full 512 budget and never cuts a long sentence.

The desk keeps those two policies as named presets so a short Sejerø brief
can be packed the same way without loading OPUS or T5.
"""

from __future__ import annotations

from dataclasses import dataclass

from sejeroe.sentences import split_sentences
from sejeroe.tokenize import LengthNotion, char_word_counter, measure

# Course constants copied from the root scripts.
OPUS_MAX_LENGTH = 512
OPUS_TEXT_MAX_LENGTH = int(OPUS_MAX_LENGTH * 0.9)  # 460
T5_TEXT_MAX_LENGTH = 512
MT5_INPUT_MAX = 1024
MT5_LABEL_MAX = 128
T5_SUMMARY_MAX = 80


@dataclass(frozen=True)
class PackPolicy:
    name: str
    budget: int
    notion: LengthNotion
    split_overflow: bool
    note: str


FORWARD_HOP = PackPolicy(
    name="forward-hop",
    budget=OPUS_TEXT_MAX_LENGTH,
    notion=LengthNotion.ROUGH_SUBWORD,
    split_overflow=True,
    note="translate.py / summary.py: 0.9 * 512 and overflow cuts on commas.",
)
BACK_HOP = PackPolicy(
    name="back-hop",
    budget=OPUS_MAX_LENGTH,
    notion=LengthNotion.ROUGH_SUBWORD,
    split_overflow=False,
    note="translate_back.py: full 512 and no long-sentence cutter.",
)
T5_SUMMARY = PackPolicy(
    name="t5-summary-cap",
    budget=T5_SUMMARY_MAX,
    notion=LengthNotion.ROUGH_SUBWORD,
    split_overflow=False,
    note="summary.py generate() max_length=80 on each packed window.",
)
MANCHET_TIGHT = PackPolicy(
    name="manchet-tight",
    budget=16,
    notion=LengthNotion.WORDS,
    split_overflow=True,
    note="Tiny word budget: a one-sentence Danish lede often still fits.",
)
MANCHET_LEAD = PackPolicy(
    name="manchet-lead",
    budget=40,
    notion=LengthNotion.WORDS,
    split_overflow=True,
    note="Word budget near a two-sentence island brief.",
)

PRESETS: dict[str, PackPolicy] = {
    policy.name: policy
    for policy in (FORWARD_HOP, BACK_HOP, T5_SUMMARY, MANCHET_TIGHT, MANCHET_LEAD)
}


@dataclass(frozen=True)
class PackedWindow:
    index: int
    sentences: tuple[str, ...]
    token_count: int
    overflow_cut: bool

    @property
    def text(self) -> str:
        return " ".join(self.sentences)


def _cut_overflow(sentence: str, budget: int, notion: LengthNotion) -> list[str]:
    """Approximate ``split_long_sentence`` from translate.py / summary.py."""
    words = sentence.split()
    chunks: list[str] = []
    current: list[str] = []
    running = 0
    for word in words:
        current.append(word)
        running += len(word) + 1
        hit_punct = word.endswith((",", ";", ":"))
        if hit_punct and running < budget:
            chunks.append(" ".join(current))
            current, running = [], 0
        elif running >= budget:
            last = current.pop()
            if current:
                chunks.append(" ".join(current))
            current, running = [last], len(last) + 1
    if current:
        chunks.append(" ".join(current))
    # The 2023 cutter does not recurse. Leftover long chunks stay intact so a
    # mixed word/character budget cannot loop. ``notion`` is accepted because
    # callers already measured with it before requesting a cut.
    _ = notion
    return chunks or [sentence]


def pack_text(text: str, policy: PackPolicy) -> list[PackedWindow]:
    raw_sentences = split_sentences(text)
    units: list[tuple[str, bool]] = []
    for sentence in raw_sentences:
        if policy.split_overflow and measure(sentence, policy.notion) > policy.budget:
            for chunk in _cut_overflow(sentence, policy.budget, policy.notion):
                units.append((chunk, True))
        else:
            units.append((sentence, False))

    windows: list[PackedWindow] = []
    current: list[str] = []
    current_len = 0
    overflow = False
    for sentence, was_cut in units:
        length = measure(sentence, policy.notion)
        if current and current_len + length > policy.budget:
            windows.append(
                PackedWindow(
                    index=len(windows),
                    sentences=tuple(current),
                    token_count=current_len,
                    overflow_cut=overflow,
                )
            )
            current, current_len, overflow = [sentence], length, was_cut
            continue
        current.append(sentence)
        current_len += length
        overflow = overflow or was_cut
    if current:
        windows.append(
            PackedWindow(
                index=len(windows),
                sentences=tuple(current),
                token_count=current_len,
                overflow_cut=overflow,
            )
        )
    return windows


def pack_report_rows(text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for policy in PRESETS.values():
        windows = pack_text(text, policy)
        rows.append(
            {
                "policy": policy.name,
                "budget": policy.budget,
                "notion": policy.notion.value,
                "windows": len(windows),
                "overflow_cuts": sum(1 for window in windows if window.overflow_cut),
                "first_window_tokens": windows[0].token_count if windows else 0,
                "note": policy.note,
            }
        )
    return rows


def char_word_len(text: str) -> int:
    return char_word_counter(text)
