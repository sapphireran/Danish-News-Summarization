"""Maalestok: a personal, download-free lab for the 2023 silver-label hops.

The December 2023 ITU scripts translate Danish news to English, summarize
with an English T5, then translate the summary back to Danish. Those hops
are especially rough on *measures*: decimal commas, thousand separators,
``kr.``, ``kl. 8.15``, signed temperatures, and Danish date words.

This package reconstructs that pipeline on a closed fictional almanac
(Blåhøj Sogn) so the attrition can be counted without OPUS-MT, T5, or a GPU.
The original root scripts are left untouched.
"""

from .measures import Measure, extract_measures, parse_da_number
from .packing import pack_article, split_long_sentence
from .sentences import split_sentences
from .world import PARISH

__all__ = [
    "PARISH",
    "Measure",
    "extract_measures",
    "pack_article",
    "parse_da_number",
    "split_long_sentence",
    "split_sentences",
]

__version__ = "0.1.0"
