"""Personal methods lab for the 2023 ITU Danish news summarization project.

Nothing here talks to a GPU, Hugging Face weights, or employer code. The
package is a notebook you can execute: Danish-aware tokenization, extractive
baselines, a from-scratch ROUGE, a hop-error catalog, and an HTML report.
"""

from .baselines import (
    BASELINE_NAMES,
    BaselineResult,
    run_all_baselines,
    summarize_keyword,
    summarize_lead,
    summarize_longest,
    summarize_textrank,
)
from .catalog import ErrorItem, load_catalog
from .fiction import Brief, iter_briefs, load_briefs
from .rouge import Score, rouge_l, rouge_n, score_pair
from .rubric import RubricScores, score_rubric
from .sentences import split_sentences
from .tokenize import content_tokens, tokenize

__all__ = [
    "BASELINE_NAMES",
    "BaselineResult",
    "Brief",
    "ErrorItem",
    "RubricScores",
    "Score",
    "content_tokens",
    "iter_briefs",
    "load_briefs",
    "load_catalog",
    "rouge_l",
    "rouge_n",
    "run_all_baselines",
    "score_pair",
    "score_rubric",
    "split_sentences",
    "summarize_keyword",
    "summarize_lead",
    "summarize_longest",
    "summarize_textrank",
    "tokenize",
]

__version__ = "0.1.0"
