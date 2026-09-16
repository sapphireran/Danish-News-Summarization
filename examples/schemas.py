"""CSV contracts for each stage of the 2023 pipeline.

The original scripts never validate columns. These dataclasses make the
same contracts explicit so a broken rename (``article text`` vs
``body``, English ``summary`` vs Danish ``summary``) fails closed in
the demos.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CsvSchema:
    name: str
    columns: tuple[str, ...]
    notes: str
    produced_by: str
    consumed_by: str

    def missing(self, fieldnames: list[str] | None) -> list[str]:
        have = set(fieldnames or [])
        return [column for column in self.columns if column not in have]


PIPELINE_SCHEMAS: dict[str, CsvSchema] = {
    "unlabeled_danish": CsvSchema(
        name="unlabeled_danish",
        columns=("id", "article text"),
        notes="translate.py input. The space in 'article text' is required.",
        produced_by="external dump (not in git)",
        consumed_by="translate.py",
    ),
    "translated": CsvSchema(
        name="translated",
        columns=("id", "body", "translated"),
        notes="Danish body plus English pivot.",
        produced_by="translate.py",
        consumed_by="summary.py",
    ),
    "english_summaries": CsvSchema(
        name="english_summaries",
        columns=("id", "body", "translated", "summary"),
        notes="summary column is English at this stage.",
        produced_by="summary.py",
        consumed_by="translate_back.py",
    ),
    "labeled_danish": CsvSchema(
        name="labeled_danish",
        columns=("id", "body", "summary"),
        notes="summary column is Danish silver labels.",
        produced_by="translate_back.py",
        consumed_by="finetune.py (after a manual split)",
    ),
    "finetune_split": CsvSchema(
        name="finetune_split",
        columns=("id", "body", "summary"),
        notes="Same columns as labeled_danish; one file per split.",
        produced_by="manual split of labeled_dataset_*.csv",
        consumed_by="finetune.py",
    ),
    "predictions": CsvSchema(
        name="predictions",
        columns=("id", "reference", "prediction"),
        notes="Example-only table for rouge_lite. Not used by eval.py.",
        produced_by="examples/data/write_tables.py",
        consumed_by="examples/run_rouge_demo.py",
    ),
}

SAMPLE_FILES: dict[str, str] = {
    "unlabeled_danish": "sample_danish_articles.csv",
    "translated": "sample_translated_articles.csv",
    "english_summaries": "sample_english_summaries.csv",
    "labeled_danish": "sample_labeled_dataset.csv",
    "predictions": "sample_predictions.csv",
}


@dataclass(frozen=True)
class ValidationResult:
    schema: CsvSchema
    path: Path
    rows: int
    ok: bool
    errors: tuple[str, ...]


def validate_csv(path: Path, schema: CsvSchema) -> ValidationResult:
    errors: list[str] = []
    rows = 0
    if not path.is_file():
        return ValidationResult(schema, path, 0, False, (f"missing file: {path}",))

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = schema.missing(reader.fieldnames)
        if missing:
            errors.append(f"missing columns: {missing}; have {reader.fieldnames}")
        for row in reader:
            rows += 1
            for column in schema.columns:
                value = (row.get(column) or "").strip()
                if not value:
                    errors.append(f"row {rows} empty column {column!r}")
                    break
            if "id" in schema.columns and not (row.get("id") or "").strip():
                errors.append(f"row {rows} has an empty id")

    if rows == 0:
        errors.append("file has a header but no data rows")
    return ValidationResult(schema, path, rows, not errors, tuple(errors))


def describe_schema(schema: CsvSchema) -> str:
    columns = ", ".join(f"`{column}`" for column in schema.columns)
    return (
        f"{schema.name}: {columns}\n"
        f"  produced by: {schema.produced_by}\n"
        f"  consumed by: {schema.consumed_by}\n"
        f"  {schema.notes}"
    )
