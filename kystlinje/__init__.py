"""Personal workbook for the 2023 Danish news summarization course project.

This package does not load OPUS-MT, T5, or mT5. It reconstructs the
silver-label hops as a handwritten fictional magazine corpus and measures
how names, places, numbers, and Danish compounds survive each hop.

The December 2023 course scripts in the repository root are left untouched.
"""

from .align import render_alignment
from .danish import normalize, split_sentences, word_tokenize
from .entities import Entity, extract_entities, entity_survives
from .ledger import HopLedger, build_ledger
from .pack import pack_article, split_long_sentence
from .schemas import COURSE_SCHEMAS

__all__ = [
    "COURSE_SCHEMAS",
    "Entity",
    "HopLedger",
    "build_ledger",
    "entity_survives",
    "extract_entities",
    "normalize",
    "pack_article",
    "render_alignment",
    "split_long_sentence",
    "split_sentences",
    "word_tokenize",
]

__version__ = "0.1.0"
