"""Helpers for the personal Danish news summarization course project.

The original course scripts stay at the repository root. This package holds
the reusable pieces those scripts share: length-aware sentence chunking and
the CSV column contracts used between pipeline stages.
"""

from .chunking import (
    DEFAULT_MAX_LENGTH,
    DEFAULT_TEXT_MAX_LENGTH_RATIO,
    chunk_article,
    split_into_sentence_batches,
    split_long_sentence,
    text_max_length,
)
from .schema import (
    LABELED_COLUMNS,
    RAW_ARTICLE_COLUMNS,
    SUMMARIZED_COLUMNS,
    TRANSLATED_COLUMNS,
    TRAIN_COLUMNS,
    required_columns,
    validate_frame,
)

__all__ = [
    "DEFAULT_MAX_LENGTH",
    "DEFAULT_TEXT_MAX_LENGTH_RATIO",
    "LABELED_COLUMNS",
    "RAW_ARTICLE_COLUMNS",
    "SUMMARIZED_COLUMNS",
    "TRANSLATED_COLUMNS",
    "TRAIN_COLUMNS",
    "chunk_article",
    "required_columns",
    "split_into_sentence_batches",
    "split_long_sentence",
    "text_max_length",
    "validate_frame",
]
