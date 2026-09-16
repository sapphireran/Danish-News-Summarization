"""CSV column contracts for every stage of the 2023 pipeline.

The root scripts hard-code column names (``article text`` vs ``body``,
``translated``, ``summary``). Getting those names wrong is the most common
reason a later script crashes after a long GPU run. Validate early.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

# Column names match the original scripts exactly, including the space in
# the raw Dansk Articles dump ("article text").
STAGE_COLUMNS: Dict[str, List[str]] = {
    "raw_articles": ["id", "article text"],
    "translated": ["id", "body", "translated"],
    "summarized": ["id", "body", "translated", "summary"],
    "labeled": ["id", "body", "summary"],
    "finetune": ["id", "body", "summary"],
}

# Human-readable description of what each column is supposed to contain.
COLUMN_HELP: Dict[str, str] = {
    "id": "Stable article identifier. Kept unchanged across every stage.",
    "article text": "Original Danish body from the news dump (raw stage only).",
    "body": "Original Danish body. Copied forward so later stages never lose source text.",
    "translated": "English translation of the Danish body (OPUS-MT da→en).",
    "summary": (
        "At the summarized stage this is still English. After translate_back.py "
        "it is Danish and becomes the fine-tuning target."
    ),
}


class SchemaError(ValueError):
    """Raised when a table or row is missing required pipeline columns."""


def required_columns(stage: str) -> List[str]:
    try:
        return list(STAGE_COLUMNS[stage])
    except KeyError as exc:
        known = ", ".join(sorted(STAGE_COLUMNS))
        raise SchemaError(f"Unknown pipeline stage {stage!r}. Known stages: {known}.") from exc


def validate_row(stage: str, row: Mapping[str, object], *, row_index: int | None = None) -> None:
    """Check that one mapping has the required keys and non-empty string values."""
    missing = [column for column in required_columns(stage) if column not in row]
    if missing:
        where = f" (row {row_index})" if row_index is not None else ""
        raise SchemaError(f"{stage} row{where} is missing columns: {missing}.")

    empty = [
        column
        for column in required_columns(stage)
        if row[column] is None or str(row[column]).strip() == ""
    ]
    if empty:
        where = f" (row {row_index})" if row_index is not None else ""
        raise SchemaError(f"{stage} row{where} has empty values for: {empty}.")


def validate_table(stage: str, rows: Sequence[Mapping[str, object]]) -> None:
    """Validate every row in a table-like sequence of mappings."""
    if not rows:
        raise SchemaError(f"{stage} table is empty.")
    for index, row in enumerate(rows):
        validate_row(stage, row, row_index=index)


def describe_stage(stage: str) -> str:
    """Return a short multi-line description of a stage's columns."""
    lines = [f"Stage '{stage}' expects columns:"]
    for column in required_columns(stage):
        help_text = COLUMN_HELP.get(column, "")
        suffix = f" — {help_text}" if help_text else ""
        lines.append(f"  - {column}{suffix}")
    return "\n".join(lines)


def project_row(stage: str, row: Mapping[str, object]) -> Dict[str, str]:
    """Return only the columns required for ``stage``, coerced to strings."""
    validate_row(stage, row)
    return {column: str(row[column]) for column in required_columns(stage)}


def iter_ids(rows: Iterable[Mapping[str, object]]) -> List[str]:
    return [str(row["id"]) for row in rows]
