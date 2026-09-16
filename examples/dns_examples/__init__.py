"""Small personal helpers for the Danish-news toy examples.

These modules do not load OPUS-MT, T5, or mT5. They exist so the
repository can show the 2023 pipeline's *shape* on fictional rows.
"""

from .chunking import (
    CharacterBudget,
    TokenCounter,
    WhitespaceCounter,
    pack_sentences,
    split_into_sentence_groups,
    split_long_sentence,
)
from .io import read_csv, write_csv
from .metrics import compression_ratio, rouge_l, rouge_n, summarize_pair
from .schema import SCHEMAS, ValidationIssue, validate_rows
from .sentences import split_sentences, word_tokenize

__all__ = [
    "CharacterBudget",
    "SCHEMAS",
    "TokenCounter",
    "ValidationIssue",
    "WhitespaceCounter",
    "compression_ratio",
    "pack_sentences",
    "read_csv",
    "rouge_l",
    "rouge_n",
    "split_into_sentence_groups",
    "split_long_sentence",
    "split_sentences",
    "summarize_pair",
    "validate_rows",
    "word_tokenize",
    "write_csv",
]
