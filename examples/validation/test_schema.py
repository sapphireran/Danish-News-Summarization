#!/usr/bin/env python3
"""Stdlib tests for CSV schema checks. Run: python examples/validation/test_schema.py"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from schema import disjoint_ids, validate_rows


def _ok_labeled() -> tuple[list[str], list[dict[str, str]]]:
    cols = ["id", "body", "summary"]
    rows = [
        {"id": "a", "body": "x" * 40, "summary": "kort"},
        {"id": "b", "body": "y" * 40, "summary": "også kort"},
    ]
    return cols, rows


class SchemaTests(unittest.TestCase):
    def test_happy_labeled(self) -> None:
        cols, rows = _ok_labeled()
        result = validate_rows(Path("mem.csv"), "labeled", cols, rows)
        self.assertTrue(result.ok, result.errors)

    def test_wrong_columns(self) -> None:
        result = validate_rows(
            Path("mem.csv"),
            "raw",
            ["id", "body"],
            [{"id": "a", "body": "hej"}],
        )
        self.assertFalse(result.ok)
        self.assertTrue(any("columns" in err for err in result.errors))

    def test_duplicate_ids(self) -> None:
        cols, rows = _ok_labeled()
        rows[1]["id"] = "a"
        result = validate_rows(Path("mem.csv"), "labeled", cols, rows)
        self.assertFalse(result.ok)
        self.assertTrue(any("duplicate" in err for err in result.errors))

    def test_empty_cell(self) -> None:
        cols, rows = _ok_labeled()
        rows[0]["summary"] = "   "
        result = validate_rows(Path("mem.csv"), "labeled", cols, rows)
        self.assertFalse(result.ok)

    def test_summary_longer_than_body(self) -> None:
        cols = ["id", "body", "summary"]
        rows = [{"id": "a", "body": "kort", "summary": "x" * 80}]
        result = validate_rows(Path("mem.csv"), "labeled", cols, rows)
        self.assertFalse(result.ok)

    def test_disjoint_ids(self) -> None:
        errors = disjoint_ids(
            (
                ("train", [{"id": "a"}]),
                ("val", [{"id": "a"}]),
            )
        )
        self.assertEqual(len(errors), 1)

    def test_roundtrip_tempfile_raw(self) -> None:
        from schema import validate_file

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.csv"
            path.write_text("id,article text\n1,hej verden det er en artikel\n", encoding="utf-8")
            result = validate_file(path, "raw")
            self.assertTrue(result.ok, result.errors)


if __name__ == "__main__":
    unittest.main()
