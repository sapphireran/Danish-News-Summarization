"""Lightweight helpers for the Danish news summarization pipeline.

The original project scripts in the repository root still run the GPU
workflow (CTranslate2 conversion, OPUS-MT, English T5, mT5 fine-tuning).
This package extracts the text-chunking and CSV-schema logic so the
``docs/`` and ``examples/`` trees can be read and executed without
downloading multi-gigabyte models.
"""

from .chunking import (
    LengthFn,
    TokenizerLike,
    WhitespaceTokenizer,
    pack_sentences_by_length,
    split_article,
    split_into_sentences,
    split_long_sentence,
    tokenize_sentences,
)
from .config import PIPELINE_STAGES, STAGE_BY_NAME, StageConfig
from .schema import STAGE_COLUMNS, SchemaError, validate_row, validate_table

__all__ = [
    "LengthFn",
    "PIPELINE_STAGES",
    "STAGE_BY_NAME",
    "STAGE_COLUMNS",
    "SchemaError",
    "StageConfig",
    "TokenizerLike",
    "WhitespaceTokenizer",
    "pack_sentences_by_length",
    "split_article",
    "split_into_sentences",
    "split_long_sentence",
    "tokenize_sentences",
    "validate_row",
    "validate_table",
]

__version__ = "0.2.0"
