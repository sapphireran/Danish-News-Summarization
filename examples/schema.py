"""CSV column contracts for each pipeline stage.

Names match the committed course scripts. Extra columns are allowed;
missing required columns are not. See docs/datasets.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

STAGE_0_ARTICLES = "articles"
STAGE_1_TRANSLATED = "translated"
STAGE_2_SUMMARIZED = "summarized"
STAGE_3_LABELED = "labeled"
STAGE_4_SPLIT = "split"

REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    STAGE_0_ARTICLES: ("id", "article text"),
    STAGE_1_TRANSLATED: ("id", "body", "translated"),
    STAGE_2_SUMMARIZED: ("id", "body", "translated", "summary"),
    STAGE_3_LABELED: ("id", "body", "summary"),
    STAGE_4_SPLIT: ("id", "body", "summary"),
}

# Columns that must be non-empty strings after strip().
NONEMPTY_COLUMNS: dict[str, tuple[str, ...]] = {
    STAGE_0_ARTICLES: ("id", "article text"),
    STAGE_1_TRANSLATED: ("id", "body", "translated"),
    STAGE_2_SUMMARIZED: ("id", "body", "translated", "summary"),
    STAGE_3_LABELED: ("id", "body", "summary"),
    STAGE_4_SPLIT: ("id", "body", "summary"),
}

SAMPLE_FILENAMES: dict[str, str] = {
    STAGE_0_ARTICLES: "00_articles_sample.csv",
    STAGE_1_TRANSLATED: "01_translated_sample.csv",
    STAGE_2_SUMMARIZED: "02_summarized_sample.csv",
    STAGE_3_LABELED: "03_labeled_sample.csv",
}

SPLIT_FILENAMES: dict[str, str] = {
    "train": "04_train_split_sample.csv",
    "validation": "04_validation_split_sample.csv",
    "test": "04_test_split_sample.csv",
}

# Names finetune.py actually opens.
FINETUNE_SPLIT_FILENAMES: dict[str, str] = {
    "train": "train_dataset.csv",
    "validation": "validation_dataset.csv",
    "test": "test_dataset.csv",
}


@dataclass(frozen=True)
class SchemaIssue:
    path: str
    kind: str
    detail: str

    def __str__(self) -> str:
        return f"{self.path}: [{self.kind}] {self.detail}"


def required_columns(stage: str) -> tuple[str, ...]:
    try:
        return REQUIRED_COLUMNS[stage]
    except KeyError as exc:
        known = ", ".join(sorted(REQUIRED_COLUMNS))
        raise ValueError(f"unknown stage {stage!r}; expected one of: {known}") from exc


def missing_columns(stage: str, header: Iterable[str]) -> list[str]:
    present = set(header)
    return [column for column in required_columns(stage) if column not in present]


def infer_stage_from_filename(name: str) -> str | None:
    """Best-effort stage guess from the course and sample filenames."""
    lowered = name.lower()
    mapping = (
        ("00_articles", STAGE_0_ARTICLES),
        ("10000_articles", STAGE_0_ARTICLES),
        ("01_translated", STAGE_1_TRANSLATED),
        ("translated_articles", STAGE_1_TRANSLATED),
        ("02_summarized", STAGE_2_SUMMARIZED),
        ("summarized_file", STAGE_2_SUMMARIZED),
        ("03_labeled", STAGE_3_LABELED),
        ("labeled_dataset", STAGE_3_LABELED),
        ("04_train", STAGE_4_SPLIT),
        ("04_validation", STAGE_4_SPLIT),
        ("04_test", STAGE_4_SPLIT),
        ("train_dataset", STAGE_4_SPLIT),
        ("validation_dataset", STAGE_4_SPLIT),
        ("test_dataset", STAGE_4_SPLIT),
    )
    for needle, stage in mapping:
        if needle in lowered:
            return stage
    return None
