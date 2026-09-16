"""CSV column contracts for every labeling / training stage.

The 2023 root scripts never validated headers. These tuples are the
documented contracts so example snapshots and future exports stay aligned.
"""

from __future__ import annotations

from typing import Mapping, Sequence

# Stage name -> exact column order expected in the matching CSV.
STAGE_COLUMNS: dict[str, tuple[str, ...]] = {
    "raw": ("id", "article text"),
    "translated": ("id", "body", "translated"),
    "summarized": ("id", "body", "translated", "summary"),
    "labeled": ("id", "body", "summary"),
    "finetune": ("id", "body", "summary"),
    "predictions": ("id", "summary"),
}

STAGE_FILES: dict[str, str] = {
    "raw": "raw_articles.csv",
    "translated": "translated_articles.csv",
    "summarized": "summarized_articles.csv",
    "labeled": "labeled_dataset.csv",
    "train": "train_dataset.csv",
    "validation": "validation_dataset.csv",
    "test": "test_dataset.csv",
    "predictions": "toy_predictions.csv",
}

# Fine-tune split files share the finetune column contract.
SPLIT_STAGE = {
    "train": "finetune",
    "validation": "finetune",
    "test": "finetune",
}

DANISH_LETTERS = frozenset("æøåÆØÅ")


class SchemaError(ValueError):
    """A CSV header or row does not match a documented stage."""


def columns_for(stage: str) -> tuple[str, ...]:
    if stage in STAGE_COLUMNS:
        return STAGE_COLUMNS[stage]
    if stage in SPLIT_STAGE:
        return STAGE_COLUMNS[SPLIT_STAGE[stage]]
    raise SchemaError(f"unknown stage {stage!r}")


def validate_headers(stage: str, headers: Sequence[str]) -> None:
    expected = list(columns_for(stage))
    got = list(headers)
    if got != expected:
        raise SchemaError(
            f"{stage} headers {got} do not match contract {expected}"
        )


def validate_row(stage: str, row: Mapping[str, str]) -> None:
    expected = columns_for(stage)
    missing = [name for name in expected if name not in row]
    if missing:
        raise SchemaError(f"{stage} row missing columns {missing}")
    empty = [name for name in expected if not str(row[name]).strip()]
    if empty:
        raise SchemaError(f"{stage} row has empty columns {empty}")


def has_danish_letters(text: str) -> bool:
    return any(char in DANISH_LETTERS for char in text)
