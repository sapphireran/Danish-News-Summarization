"""Character-plus-one vs approx-subword budgets on one article.

The 2023 long-sentence splitter counts ``len(word) + 1``. The packer counts
``tokenizer.encode`` pieces. This module prints both on the same windows so
the mismatch is visible without Helsinki-NLP weights.
"""

from __future__ import annotations

from dataclasses import dataclass

from .article import Article
from .packing import pack_article
from .tokenize import approx_subword_len, char_plus_one_len, word_tokenize


@dataclass(frozen=True)
class BudgetRow:
    index: int
    preview: str
    char_plus_one: int
    approx_tokens: int
    ratio: float


def compare_budgets(article: Article, budget: int = 80) -> list[BudgetRow]:
    windows = pack_article(article.body_da, budget=budget)
    rows: list[BudgetRow] = []
    for window in windows:
        char_len = char_plus_one_len(word_tokenize(window.text))
        tok_len = approx_subword_len(window.text)
        rows.append(
            BudgetRow(
                index=window.index,
                preview=window.text[:72] + ("…" if len(window.text) > 72 else ""),
                char_plus_one=char_len,
                approx_tokens=tok_len,
                ratio=(tok_len / char_len) if char_len else 0.0,
            )
        )
    return rows
