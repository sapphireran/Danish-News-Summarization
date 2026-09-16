"""Structural checks for the pipeline CSVs.

These catch broken column names and empty cells. They do not detect
translationese, hallucinations, or language-id mistakes.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

STAGE_COLUMNS: dict[str, tuple[str, ...]] = {
    "raw": ("id", "article text"),
    "translated": ("id", "body", "translated"),
    "summarized": ("id", "body", "translated", "summary"),
    "labeled": ("id", "body", "summary"),
}

# After translate.py the Danish text lives in `body`.
BODY_COLUMNS = ("article text", "body")


@dataclass
class CheckResult:
    path: Path
    stage: str
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    n_rows: int = 0

    def lines(self) -> list[str]:
        tag = "OK" if self.ok else "FAIL"
        header = f"[{tag}] {self.path} ({self.stage}, {self.n_rows} rows)"
        out = [header]
        for item in self.errors:
            out.append(f"  error: {item}")
        for item in self.warnings:
            out.append(f"  warn:  {item}")
        return out


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header")
        fieldnames = [name.strip() for name in reader.fieldnames]
        rows = [{k.strip(): (v or "") for k, v in row.items() if k} for row in reader]
    return fieldnames, rows


def _body(row: Mapping[str, str]) -> str:
    for key in BODY_COLUMNS:
        if key in row and row[key].strip():
            return row[key]
    return ""


def validate_rows(
    path: Path,
    stage: str,
    fieldnames: Sequence[str],
    rows: Sequence[Mapping[str, str]],
    *,
    require_summary_shorter: bool = True,
) -> CheckResult:
    expected = STAGE_COLUMNS[stage]
    errors: list[str] = []
    warnings: list[str] = []

    if tuple(fieldnames) != expected:
        errors.append(f"columns {list(fieldnames)} != expected {list(expected)}")

    ids = [row.get("id", "") for row in rows]
    if any(not item.strip() for item in ids):
        errors.append("one or more empty id values")
    if len(ids) != len(set(ids)):
        seen: set[str] = set()
        dupes = []
        for item in ids:
            if item in seen and item not in dupes:
                dupes.append(item)
            seen.add(item)
        errors.append(f"duplicate ids: {dupes}")

    for i, row in enumerate(rows, start=1):
        for col in expected:
            value = row.get(col, "")
            if not str(value).strip():
                errors.append(f"row {i} ({row.get('id', '?')}) empty column {col!r}")

        body = _body(row)
        if "summary" in expected and body and row.get("summary", "").strip():
            if require_summary_shorter and len(row["summary"]) >= len(body):
                errors.append(
                    f"row {i} ({row.get('id')}) summary is not shorter than body "
                    f"({len(row['summary'])} >= {len(body)})"
                )
        if stage == "summarized":
            if row.get("summary") and row.get("translated"):
                if len(row["summary"]) >= len(row["translated"]):
                    warnings.append(
                        f"row {i} ({row.get('id')}) English summary is not shorter "
                        f"than the English article"
                    )

    return CheckResult(
        path=path,
        stage=stage,
        ok=not errors,
        errors=errors,
        warnings=warnings,
        n_rows=len(rows),
    )


def validate_file(path: Path, stage: str, **kwargs) -> CheckResult:
    fieldnames, rows = read_rows(path)
    return validate_rows(path, stage, fieldnames, rows, **kwargs)


def disjoint_ids(parts: Iterable[tuple[str, Sequence[Mapping[str, str]]]]) -> list[str]:
    """Return error strings if the same id appears in more than one split."""
    owner: dict[str, str] = {}
    errors: list[str] = []
    for name, rows in parts:
        for row in rows:
            article_id = row["id"]
            if article_id in owner:
                errors.append(
                    f"id {article_id!r} in both {owner[article_id]} and {name}"
                )
            else:
                owner[article_id] = name
    return errors
