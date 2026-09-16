"""Helpers extracted from the 2023 ITU Danish news summarization project.

The original training and translation scripts still live at the repository
root. This package is the documented, testable subset used by ``docs/`` and
``examples/``: article chunking, silver-label CSV I/O, and lexical metrics
that can run without downloading mT5 or OPUS-MT.
"""

from danish_news_sum.chunking import (
    pack_sentences,
    split_article,
    split_into_sentences,
    split_long_sentence,
)
from danish_news_sum.dataset import (
    SILVER_COLUMNS,
    DatasetStats,
    load_article_csv,
    summarize_dataset,
    validate_columns,
)
from danish_news_sum.metrics import (
    compression_ratio,
    lcs_f1,
    lexical_scores,
    ngram_f1,
    token_overlap,
)

__all__ = [
    "SILVER_COLUMNS",
    "DatasetStats",
    "compression_ratio",
    "lcs_f1",
    "lexical_scores",
    "load_article_csv",
    "ngram_f1",
    "pack_sentences",
    "split_article",
    "split_into_sentences",
    "split_long_sentence",
    "summarize_dataset",
    "token_overlap",
    "validate_columns",
]

__version__ = "0.2.0"
