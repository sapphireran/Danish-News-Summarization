from pathlib import Path

import pytest

from danish_news_sum.dataset import (
    SILVER_COLUMNS,
    load_article_csv,
    summarize_dataset,
    validate_columns,
    window_plan,
    write_article_csv,
)


def test_roundtrip_csv(tmp_path: Path):
    rows = [
        {"id": "ex-1", "body": "Kort artikel om Aarhus.", "summary": "Aarhus nyt."},
        {"id": "ex-2", "body": "Endnu en artikel.", "summary": "Kort."},
    ]
    path = tmp_path / "silver.csv"
    write_article_csv(path, rows, SILVER_COLUMNS)
    loaded = load_article_csv(path)
    assert loaded == rows


def test_validate_columns_reports_missing_fields():
    with pytest.raises(ValueError, match="missing columns"):
        validate_columns([{"id": "1"}], required=SILVER_COLUMNS, label="silver")


def test_summarize_dataset_counts_tokens():
    rows = [
        {
            "id": "ex-1",
            "body": "Første lange artikel om metroen i København og de nye stationer.",
            "summary": "Ny metro i København.",
        }
    ]
    stats = summarize_dataset(rows)
    assert stats.rows == 1
    assert stats.empty_bodies == 0
    assert stats.mean_body_tokens > stats.mean_summary_tokens
    assert stats.mean_compression > 1.0


def test_window_plan_uses_body_column():
    rows = [
        {
            "id": "ex-1",
            "body": "Første sætning om fiskeri. Anden sætning om Vestkysten. Tredje sætning om torsk.",
        }
    ]
    plan = window_plan(rows, text_max_length=10)
    assert plan[0]["id"] == "ex-1"
    assert plan[0]["window_count"] >= 1
    assert plan[0]["windows"]
