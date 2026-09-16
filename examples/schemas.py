"""CSV column contracts for every pipeline stage.

The root scripts hard-code these names. Keeping them in one place lets
sample files and tests fail loudly when a header drifts.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

RAW_COLUMNS = ("id", "article text")
TRANSLATED_COLUMNS = ("id", "body", "translated")
SUMMARIZED_COLUMNS = ("id", "body", "translated", "summary")
LABELED_COLUMNS = ("id", "body", "summary")
SPLIT_COLUMNS = LABELED_COLUMNS

STAGE_COLUMNS = {
    "raw": RAW_COLUMNS,
    "translated": TRANSLATED_COLUMNS,
    "summarized": SUMMARIZED_COLUMNS,
    "labeled": LABELED_COLUMNS,
    "split": SPLIT_COLUMNS,
}

SAMPLE_STEM_TO_STAGE = {
    "00_raw_articles": "raw",
    "01_translated_articles": "translated",
    "02_summarized_articles": "summarized",
    "03_labeled_dataset": "labeled",
    "04_train_dataset": "split",
    "04_validation_dataset": "split",
    "04_test_dataset": "split",
}


class SchemaError(ValueError):
    """A CSV does not match the stage contract."""


def _missing_or_empty(row: Mapping[str, str], columns: Sequence[str]) -> List[str]:
    bad = []
    for column in columns:
        value = row.get(column)
        if value is None or not str(value).strip():
            bad.append(column)
    return bad


def validate_rows(
    rows: Iterable[Mapping[str, object]],
    columns: Sequence[str],
    *,
    stage: str = "table",
    require_unique_ids: bool = True,
) -> List[Dict[str, str]]:
    """Return normalized string rows or raise ``SchemaError``."""
    cleaned: List[Dict[str, str]] = []
    seen_ids = set()
    for index, row in enumerate(rows, start=1):
        as_str = {str(key): "" if value is None else str(value) for key, value in row.items()}
        missing = [column for column in columns if column not in as_str]
        if missing:
            raise SchemaError(f"{stage} row {index} is missing columns: {missing}")
        empty = _missing_or_empty(as_str, columns)
        if empty:
            raise SchemaError(f"{stage} row {index} has empty fields: {empty}")
        ident = as_str["id"].strip()
        if require_unique_ids and ident in seen_ids:
            raise SchemaError(f"{stage} has duplicate id {ident!r}")
        seen_ids.add(ident)
        cleaned.append({column: as_str[column].strip() for column in columns})
    if not cleaned:
        raise SchemaError(f"{stage} has no rows")
    return cleaned


def read_csv(path: Path | str) -> List[Dict[str, str]]:
    csv_path = Path(path)
    with csv_path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path | str, rows: Sequence[Mapping[str, str]], columns: Sequence[str]) -> None:
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in columns})


def validate_csv(path: Path | str, columns: Sequence[str], *, stage: str | None = None) -> List[Dict[str, str]]:
    csv_path = Path(path)
    label = stage or csv_path.name
    rows = read_csv(csv_path)
    header = list(rows[0].keys()) if rows else []
    extra = [name for name in header if name not in columns]
    missing = [name for name in columns if name not in header]
    if missing:
        raise SchemaError(f"{label} is missing columns {missing}; found {header}")
    if extra:
        # Extra columns are allowed in raw dumps but dropped later. Flag them
        # so sample files stay minimal and easy to read.
        raise SchemaError(f"{label} has unexpected columns {extra}; expected {list(columns)}")
    return validate_rows(rows, columns, stage=label)


def infer_stage(path: Path | str) -> str:
    stem = Path(path).stem
    if stem in SAMPLE_STEM_TO_STAGE:
        return SAMPLE_STEM_TO_STAGE[stem]
    raise SchemaError(f"cannot infer stage from filename {Path(path).name}")


def validate_sample_dir(directory: Path | str) -> Dict[str, int]:
    """Validate every known sample CSV. Returns row counts by filename."""
    root = Path(directory)
    counts: Dict[str, int] = {}
    for stem, stage in SAMPLE_STEM_TO_STAGE.items():
        path = root / f"{stem}.csv"
        if not path.exists():
            raise SchemaError(f"missing sample file {path}")
        rows = validate_csv(path, STAGE_COLUMNS[stage], stage=stem)
        counts[path.name] = len(rows)
    _assert_sample_id_flow(root)
    return counts


def _assert_sample_id_flow(root: Path) -> None:
    """Ids must be stable from raw → labeled, then partition into splits."""
    raw_ids = {row["id"] for row in read_csv(root / "00_raw_articles.csv")}
    translated_ids = {row["id"] for row in read_csv(root / "01_translated_articles.csv")}
    summarized_ids = {row["id"] for row in read_csv(root / "02_summarized_articles.csv")}
    labeled_ids = {row["id"] for row in read_csv(root / "03_labeled_dataset.csv")}
    if raw_ids != translated_ids or raw_ids != summarized_ids or raw_ids != labeled_ids:
        raise SchemaError("sample ids do not match across raw/translated/summarized/labeled")

    split_ids = []
    for name in ("04_train_dataset.csv", "04_validation_dataset.csv", "04_test_dataset.csv"):
        split_ids.extend(row["id"] for row in read_csv(root / name))
    if set(split_ids) != labeled_ids:
        raise SchemaError("train/validation/test ids must be a partition of labeled ids")
    if len(split_ids) != len(set(split_ids)):
        raise SchemaError("an id appears in more than one split")
