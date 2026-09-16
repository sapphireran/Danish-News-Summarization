"""CSV contracts, including the space in hop-0 `article text`."""

from __future__ import annotations

import pytest

from pakhus.export import write_lab_data
from pakhus.hops import run_corpus
from pakhus.schemas import HOP0_RAW, SchemaError, assert_article_text_column, validate_row, validate_table


def test_hop0_rejects_underscore_name() -> None:
    with pytest.raises(SchemaError):
        assert_article_text_column(["id", "article_text"])


def test_hop0_requires_space() -> None:
    assert_article_text_column(["id", "article text"])
    problems = validate_row(HOP0_RAW, {"id": "x", "article_text": "hej"})
    assert any("article text" in p or "article_text" in p for p in problems)


def test_hop0_empty_body() -> None:
    problems = validate_row(HOP0_RAW, {"id": "x", "article text": "  "})
    assert problems


def test_generated_tables_match_contracts(tmp_path) -> None:
    cascade = run_corpus()
    written = write_lab_data(tmp_path, cascade)
    from pakhus.csvio import read_dicts

    rows = read_dicts(written["hop0_raw"])
    assert "article text" in rows[0]
    assert "article_text" not in rows[0]
    assert validate_table(HOP0_RAW, rows) == []
    assert len(rows) == 10
