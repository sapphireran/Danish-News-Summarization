"""Helpers for the personal Danish news summarization project.

The 2023 ITU course scripts in the repository root are left intact.
This package extracts the reusable pieces those scripts share — sentence
packing, CSV stage schemas, and reference-free / reference-based scoring —
so documentation and examples can run without downloading translation or
summarization checkpoints.
"""

from danish_news.chunking import (
    pack_windows,
    split_long_sentence,
    split_sentences,
    split_into_windows,
)
from danish_news.schemas import STAGE_SCHEMAS, validate_rows
from danish_news.scoring import (
    compression_ratio,
    novelty_rate,
    rouge_n,
    rouge_l,
    score_pair,
    tokenize,
)

__all__ = [
    "STAGE_SCHEMAS",
    "compression_ratio",
    "novelty_rate",
    "pack_windows",
    "rouge_l",
    "rouge_n",
    "score_pair",
    "split_into_windows",
    "split_long_sentence",
    "split_sentences",
    "tokenize",
    "validate_rows",
]

__version__ = "0.2.0"
