"""CSV column contracts for each stage of the 2023 pipeline.

The course scripts hand off files by convention rather than by schema:

* raw scrape → `id`, `article text`
* after DA→EN → `id`, `body`, `translated`
* after English summarization → `id`, `body`, `translated`, `summary`
* after EN→DA (silver labels) → `id`, `body`, `summary`
* Nordjylland / ScandEval eval split → `input_text`, `target_text`, plus lengths

Examples and tests import these contracts so a renamed column fails loudly
instead of writing an empty series into the next script.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class StageSchema:
    name: str
    columns: tuple[str, ...]
    required: tuple[str, ...]
    description: str

    def missing(self, columns: Iterable[str]) -> list[str]:
        have = set(columns)
        return [column for column in self.required if column not in have]


STAGE_SCHEMAS: dict[str, StageSchema] = {
    "raw": StageSchema(
        name="raw",
        columns=("id", "article text"),
        required=("id", "article text"),
        description="Danish articles as scraped or exported before translation.",
    ),
    "translated": StageSchema(
        name="translated",
        columns=("id", "body", "translated"),
        required=("id", "body", "translated"),
        description="Original Danish body plus the OPUS-MT DA→EN translation.",
    ),
    "summarized_en": StageSchema(
        name="summarized_en",
        columns=("id", "body", "translated", "summary"),
        required=("id", "body", "translated", "summary"),
        description="English T5 summaries still paired with the Danish body.",
    ),
    "labeled": StageSchema(
        name="labeled",
        columns=("id", "body", "summary"),
        required=("id", "body", "summary"),
        description="Silver Danish labels used to fine-tune mT5.",
    ),
    "finetune_split": StageSchema(
        name="finetune_split",
        columns=("id", "body", "summary"),
        required=("id", "body", "summary"),
        description="Train / validation / test CSVs consumed by finetune.py.",
    ),
    "scandeval": StageSchema(
        name="scandeval",
        columns=("input_text", "target_text", "text_len", "summary_len"),
        required=("input_text", "target_text"),
        description="Nordjylland news rows as loaded in use_model.py / eval.py.",
    ),
}

# Human names used in the original scripts, kept here so docs can refer to one
# place when describing the on-disk handoff.
DEFAULT_FILENAMES = {
    "raw": "10000_articles_without_linebreaks.csv",
    "translated": "translated_articles.csv",
    "summarized_en": "summarized_file_ml80_rp5.0.csv",
    "labeled": "labeled_dataset_ml80_rp5.0.csv",
    "train": "datasets/train_dataset.csv",
    "validation": "datasets/validation_dataset.csv",
    "test": "datasets/test_dataset.csv",
}


class SchemaError(ValueError):
    """A CSV does not match the stage it was claimed to be."""


def validate_rows(
    rows: Sequence[Mapping[str, object]],
    stage: str,
    *,
    allow_extra: bool = True,
) -> list[dict[str, str]]:
    """Validate in-memory rows and return a normalized list of string dicts."""
    schema = _schema(stage)
    if not rows:
        raise SchemaError(f"{schema.name} stage has no rows")

    normalized: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        missing = schema.missing(row.keys())
        if missing:
            raise SchemaError(
                f"{schema.name} row {index} is missing columns: {', '.join(missing)}"
            )
        extra = [key for key in row.keys() if key not in schema.columns]
        if extra and not allow_extra:
            raise SchemaError(
                f"{schema.name} row {index} has unexpected columns: {', '.join(extra)}"
            )
        empty_required = [
            key for key in schema.required if _is_empty(row.get(key))
        ]
        if empty_required:
            raise SchemaError(
                f"{schema.name} row {index} has empty required fields: "
                f"{', '.join(empty_required)}"
            )
        normalized.append({key: "" if row.get(key) is None else str(row[key]) for key in row})
    return normalized


def read_csv(path: str | Path, stage: str, *, allow_extra: bool = True) -> list[dict[str, str]]:
    """Load a stage CSV and validate it."""
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        if reader.fieldnames is None:
            raise SchemaError(f"{csv_path} has no header row")
        missing = _schema(stage).missing(reader.fieldnames)
        if missing:
            raise SchemaError(
                f"{csv_path} is missing columns for {stage}: {', '.join(missing)}"
            )
    return validate_rows(rows, stage, allow_extra=allow_extra)


def write_csv(path: str | Path, rows: Sequence[Mapping[str, object]], stage: str) -> Path:
    """Validate rows and write them with the stage's canonical column order."""
    schema = _schema(stage)
    validated = validate_rows(rows, stage)
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(schema.columns)
    extras = [
        key
        for row in validated
        for key in row
        if key not in fieldnames
    ]
    for key in extras:
        if key not in fieldnames:
            fieldnames.append(key)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in validated:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return csv_path


def _schema(stage: str) -> StageSchema:
    try:
        return STAGE_SCHEMAS[stage]
    except KeyError as exc:
        known = ", ".join(sorted(STAGE_SCHEMAS))
        raise SchemaError(f"unknown stage {stage!r}; expected one of: {known}") from exc


def _is_empty(value: object) -> bool:
    if value is None:
        return True
    return str(value).strip() == ""
