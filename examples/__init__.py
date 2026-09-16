"""Lightweight demos for the Danish news summarization course project."""

from examples.rouge_lite import rouge_corpus, rouge_scores
from examples.schemas import PIPELINE_SCHEMAS, validate_csv
from examples.text_chunking import SimpleWordTokenizer, split_article

__all__ = [
    "PIPELINE_SCHEMAS",
    "SimpleWordTokenizer",
    "rouge_corpus",
    "rouge_scores",
    "split_article",
    "validate_csv",
]
