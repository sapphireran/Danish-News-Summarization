"""CSV contracts copied from the December 2023 scripts.

``finetune.py`` never records how ``labeled_dataset_*.csv`` became
``datasets/train_dataset.csv``. The split is a later, local convention.
"""

from __future__ import annotations

from dataclasses import dataclass

STAGE_COLUMNS: dict[str, tuple[str, ...]] = {
    "raw": ("id", "article text"),
    "translated": ("id", "body", "translated"),
    "summarized": ("id", "body", "translated", "summary"),
    "labeled": ("id", "body", "summary"),
    "finetune": ("id", "body", "summary"),
    "public_eval": ("input_text", "target_text", "text_len", "summary_len"),
}


@dataclass(frozen=True)
class SchemaError:
    stage: str
    message: str


def check_headers(stage: str, headers: list[str]) -> list[SchemaError]:
    expected = list(STAGE_COLUMNS[stage])
    errors: list[SchemaError] = []
    if headers != expected:
        errors.append(
            SchemaError(
                stage,
                f"expected {expected}, got {headers}",
            )
        )
    return errors


def check_row(stage: str, row: dict[str, str]) -> list[SchemaError]:
    errors: list[SchemaError] = []
    for col in STAGE_COLUMNS[stage]:
        if not str(row.get(col, "")).strip():
            errors.append(SchemaError(stage, f"empty {col!r}"))
    return errors
