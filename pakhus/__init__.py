"""Pakhuset: a CPU packing-house lab for the 2023 Danish summarization scripts.

The original course files in the repository root are a frozen exam snapshot.
This package reconstructs their windowing, CSV contracts, and known scars
without downloading OPUS-MT, T5, or mT5.
"""

from __future__ import annotations

from pakhus.packing import (
    Pane,
    pack_consistent,
    pack_course_back,
    pack_course_summary,
    pack_course_translate,
)
from pakhus.sentences import split_danish, split_naive
from pakhus.tokenize import approx_encode_len, word_tokenize

__all__ = [
    "Pane",
    "approx_encode_len",
    "pack_consistent",
    "pack_course_back",
    "pack_course_summary",
    "pack_course_translate",
    "split_danish",
    "split_naive",
    "word_tokenize",
]

__version__ = "0.1.0"
