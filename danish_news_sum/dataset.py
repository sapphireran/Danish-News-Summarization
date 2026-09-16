"""CSV helpers for the silver-label pipeline and the committed example fixtures."""

from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from danish_news_sum.chunking import simple_sent_tokenize, whitespace_token_count
from danish_news_sum.metrics import tokenize

# Column names used across the 2023 scripts and the example fixtures.
RAW_COLUMNS = ("id", "article text")
TRANSLATED_COLUMNS = ("id", "body", "translated")
SUMMARIZED_COLUMNS = ("id", "body", "translated", "summary")
SILVER_COLUMNS = ("id", "body", "summary")
EVAL_COLUMNS = ("id", "input_text", "target_text", "prediction")


@dataclass(frozen=True)
class DatasetStats:
    rows: int
    empty_bodies: int
    empty_summaries: int
    mean_body_tokens: float
    mean_summary_tokens: float
    mean_compression: float
    mean_sentences: float
    ids: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "rows": self.rows,
            "empty_bodies": self.empty_bodies,
            "empty_summaries": self.empty_summaries,
            "mean_body_tokens": round(self.mean_body_tokens, 2),
            "mean_summary_tokens": round(self.mean_summary_tokens, 2),
            "mean_compression": round(self.mean_compression, 2),
            "mean_sentences": round(self.mean_sentences, 2),
        }


def load_article_csv(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{csv_path} has no header row")
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    return rows


def write_article_csv(path: str | Path, rows: Sequence[dict[str, str]], columns: Sequence[str]) -> None:
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def validate_columns(rows: Sequence[dict[str, str]], required: Sequence[str], label: str = "dataset") -> None:
    if not rows:
        raise ValueError(f"{label} is empty")
    missing = [column for column in required if column not in rows[0]]
    if missing:
        raise ValueError(f"{label} is missing columns {missing}; have {sorted(rows[0])}")


def _mean(values: Iterable[float]) -> float:
    materialised = list(values)
    if not materialised:
        return 0.0
    return sum(materialised) / len(materialised)


def summarize_dataset(
    rows: Sequence[dict[str, str]],
    body_field: str = "body",
    summary_field: str = "summary",
) -> DatasetStats:
    body_tokens = [len(tokenize(row.get(body_field, ""))) for row in rows]
    summary_tokens = [len(tokenize(row.get(summary_field, ""))) for row in rows]
    compressions = [
        (body / summary) if summary else 0.0
        for body, summary in zip(body_tokens, summary_tokens, strict=True)
    ]
    sentences = [len(simple_sent_tokenize(row.get(body_field, ""))) for row in rows]
    return DatasetStats(
        rows=len(rows),
        empty_bodies=sum(1 for tokens in body_tokens if tokens == 0),
        empty_summaries=sum(1 for tokens in summary_tokens if tokens == 0),
        mean_body_tokens=_mean(body_tokens),
        mean_summary_tokens=_mean(summary_tokens),
        mean_compression=_mean(compressions),
        mean_sentences=_mean(sentences),
        ids=tuple(row.get("id", "") for row in rows),
    )


def body_field_for(rows: Sequence[dict[str, str]]) -> str:
    """Pick the article-body column used by a given pipeline stage CSV."""
    for candidate in ("body", "article text", "input_text"):
        if rows and candidate in rows[0]:
            return candidate
    raise ValueError("Could not find a body column among body / article text / input_text")


def window_plan(rows: Sequence[dict[str, str]], text_max_length: int = 80) -> list[dict[str, object]]:
    """Describe how each article would be packed for translation or summarization."""
    from danish_news_sum.chunking import describe_windows

    field_name = body_field_for(rows)
    plan: list[dict[str, object]] = []
    for row in rows:
        windows = describe_windows(row.get(field_name, ""), text_max_length=text_max_length)
        plan.append(
            {
                "id": row.get("id", ""),
                "body_tokens": whitespace_token_count(row.get(field_name, "")),
                "window_count": len(windows),
                "windows": windows,
            }
        )
    return plan
