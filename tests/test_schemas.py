from __future__ import annotations

import pytest

from danish_news.schemas import (
    STAGE_SCHEMAS,
    SchemaError,
    read_csv,
    validate_rows,
    write_csv,
)


def test_raw_rows_roundtrip(tmp_path) -> None:
    rows = [{"id": "wx-aarhus", "article text": "Skyerne letter over Aarhus."}]
    path = write_csv(tmp_path / "raw.csv", rows, "raw")
    loaded = read_csv(path, "raw")
    assert loaded[0]["id"] == "wx-aarhus"
    assert "letter" in loaded[0]["article text"]


def test_missing_column_raises() -> None:
    with pytest.raises(SchemaError, match="missing columns"):
        validate_rows([{"id": "1"}], "raw")


def test_empty_required_field_raises() -> None:
    with pytest.raises(SchemaError, match="empty required"):
        validate_rows([{"id": "1", "article text": "  "}], "raw")


def test_unknown_stage() -> None:
    with pytest.raises(SchemaError, match="unknown stage"):
        validate_rows([{"id": "1"}], "nope")


def test_labeled_schema_columns() -> None:
    schema = STAGE_SCHEMAS["labeled"]
    assert schema.columns == ("id", "body", "summary")


def test_scandeval_allows_length_columns() -> None:
    rows = [
        {
            "input_text": "artikel",
            "target_text": "resume",
            "text_len": "12",
            "summary_len": "4",
        }
    ]
    validated = validate_rows(rows, "scandeval")
    assert validated[0]["input_text"] == "artikel"


def test_extra_columns_rejected_when_asked() -> None:
    rows = [
        {"id": "1", "body": "a", "summary": "b", "extra": "nope"}
    ]
    with pytest.raises(SchemaError, match="unexpected"):
        validate_rows(rows, "labeled", allow_extra=False)
