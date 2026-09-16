"""Column contracts for every CSV the 2023 scripts read or write."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

# Exact headers, including the space in `article text`.
SCHEMAS: dict[str, tuple[str, ...]] = {
    "articles": ("id", "article text"),
    "translated": ("id", "body", "translated"),
    "summaries_en": ("id", "body", "translated", "summary"),
    "labeled": ("id", "body", "summary"),
}

# Human names used in error messages.
STAGE_LABELS = {
    "articles": "stage 0 unlabeled Danish (translate.py input)",
    "translated": "stage 1 DA→EN (translate.py output)",
    "summaries_en": "stage 2 English summaries (summary.py output)",
    "labeled": "stage 3 silver Danish pairs (translate_back.py output)",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    row_id: str | None = None
    column: str | None = None

    def __str__(self) -> str:
        bits = [self.code]
        if self.row_id:
            bits.append(f"id={self.row_id}")
        if self.column:
            bits.append(f"col={self.column}")
        return f"{' '.join(bits)}: {self.message}"


@dataclass
class ValidationReport:
    stage: str
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.issues

    def add(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)


def header_of(rows_or_fieldnames: Sequence[str] | None) -> tuple[str, ...]:
    if not rows_or_fieldnames:
        return ()
    return tuple(rows_or_fieldnames)


def validate_rows(
    rows: Sequence[Mapping[str, str]],
    stage: str,
    *,
    fieldnames: Sequence[str] | None = None,
    allow_extra: bool = False,
) -> ValidationReport:
    """Check one table against `SCHEMAS[stage]`."""
    if stage not in SCHEMAS:
        raise KeyError(f"unknown stage {stage!r}; expected one of {sorted(SCHEMAS)}")

    report = ValidationReport(stage=stage)
    expected = SCHEMAS[stage]
    if fieldnames is not None:
        actual = tuple(fieldnames)
        missing = [name for name in expected if name not in actual]
        extra = [name for name in actual if name not in expected]
        if missing:
            report.add(ValidationIssue("missing_columns", f"missing {missing}; expected {list(expected)}"))
        if extra and not allow_extra:
            report.add(ValidationIssue("extra_columns", f"unexpected {extra}; expected {list(expected)}"))

    seen: dict[str, int] = {}
    for index, row in enumerate(rows, start=1):
        row_id = str(row.get("id") or "").strip()
        if not row_id:
            report.add(ValidationIssue("empty_id", f"row {index} has an empty id", column="id"))
            continue
        if row_id in seen:
            report.add(
                ValidationIssue(
                    "duplicate_id",
                    f"id repeats (first seen on row {seen[row_id]})",
                    row_id=row_id,
                    column="id",
                )
            )
        else:
            seen[row_id] = index
        for column in expected:
            if column == "id":
                continue
            value = row.get(column)
            if value is None or str(value).strip() == "":
                report.add(
                    ValidationIssue(
                        "empty_cell",
                        f"required cell is empty on row {index}",
                        row_id=row_id,
                        column=column,
                    )
                )
    return report


def align_id_sets(
    left: Iterable[str],
    right: Iterable[str],
    *,
    left_name: str,
    right_name: str,
) -> list[ValidationIssue]:
    left_set, right_set = set(left), set(right)
    issues: list[ValidationIssue] = []
    only_left = sorted(left_set - right_set)
    only_right = sorted(right_set - left_set)
    if only_left:
        issues.append(
            ValidationIssue(
                "id_mismatch",
                f"ids in {left_name} missing from {right_name}: {only_left}",
            )
        )
    if only_right:
        issues.append(
            ValidationIssue(
                "id_mismatch",
                f"ids in {right_name} missing from {left_name}: {only_right}",
            )
        )
    return issues


def validate_split_partition(
    labeled_ids: Iterable[str],
    train_ids: Iterable[str],
    validation_ids: Iterable[str],
    test_ids: Iterable[str],
) -> list[ValidationIssue]:
    labeled = set(labeled_ids)
    train, validation, test = set(train_ids), set(validation_ids), set(test_ids)
    issues: list[ValidationIssue] = []

    for name, group in (("train", train), ("validation", validation), ("test", test)):
        unknown = sorted(group - labeled)
        if unknown:
            issues.append(
                ValidationIssue("split_unknown_id", f"{name} contains ids not in labeled: {unknown}")
            )

    overlap_tv = sorted(train & validation)
    overlap_tt = sorted(train & test)
    overlap_vt = sorted(validation & test)
    if overlap_tv:
        issues.append(ValidationIssue("split_overlap", f"train ∩ validation = {overlap_tv}"))
    if overlap_tt:
        issues.append(ValidationIssue("split_overlap", f"train ∩ test = {overlap_tt}"))
    if overlap_vt:
        issues.append(ValidationIssue("split_overlap", f"validation ∩ test = {overlap_vt}"))

    missing = sorted(labeled - (train | validation | test))
    if missing:
        issues.append(ValidationIssue("split_incomplete", f"labeled ids not in any split: {missing}"))
    return issues
