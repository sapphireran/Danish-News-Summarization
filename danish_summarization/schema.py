"""CSV column contracts between the personal course-project stages.

The original scripts hard-code file names and column lists. Keeping the
contracts here makes the examples and docs agree with those scripts without
rewriting them.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

RAW_ARTICLE_COLUMNS = ("id", "article text")
TRANSLATED_COLUMNS = ("id", "body", "translated")
SUMMARIZED_COLUMNS = ("id", "body", "translated", "summary")
LABELED_COLUMNS = ("id", "body", "summary")
TRAIN_COLUMNS = ("id", "body", "summary")

STAGE_COLUMNS = {
    "raw": RAW_ARTICLE_COLUMNS,
    "translated": TRANSLATED_COLUMNS,
    "summarized": SUMMARIZED_COLUMNS,
    "labeled": LABELED_COLUMNS,
    "train": TRAIN_COLUMNS,
}

FILE_HINTS = {
    "raw": "10000_articles_without_linebreaks.csv",
    "translated": "translated_articles.csv",
    "summarized": "summarized_file_ml80_rp5.0.csv",
    "labeled": "labeled_dataset_ml80_rp5.0.csv",
    "train": "datasets/train_dataset.csv",
    "validation": "datasets/validation_dataset.csv",
    "test": "datasets/test_dataset.csv",
}


def required_columns(stage: str) -> tuple[str, ...]:
    """Return the expected columns for a pipeline stage name."""
    try:
        return STAGE_COLUMNS[stage]
    except KeyError as exc:
        known = ", ".join(sorted(STAGE_COLUMNS))
        raise ValueError(f"unknown stage {stage!r}; expected one of: {known}") from exc


def missing_columns(columns: Iterable[str], stage: str) -> list[str]:
    """Return required columns that are absent from ``columns``."""
    present = set(columns)
    return [name for name in required_columns(stage) if name not in present]


def validate_frame(frame: Mapping[str, Sequence], stage: str) -> list[str]:
    """Validate that a mapping-like table has the columns for ``stage``.

    Returns a list of problem strings. An empty list means the table matches
    the contract. This keeps the helper usable from scripts that do not want
    to raise on the first missing column.
    """
    problems: list[str] = []
    missing = missing_columns(frame.keys(), stage)
    if missing:
        problems.append(
            f"{stage} table is missing columns: {', '.join(missing)}"
        )

    if "id" in frame:
        ids = list(frame["id"])
        if len(ids) != len(set(map(str, ids))):
            problems.append(f"{stage} table has duplicate id values")

    return problems
