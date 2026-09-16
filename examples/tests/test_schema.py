"""Schema contracts and committed snapshot headers."""

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXAMPLES_DIR))

from schema import (  # noqa: E402
    STAGE_COLUMNS,
    STAGE_FILES,
    SchemaError,
    columns_for,
    has_danish_letters,
    validate_headers,
    validate_row,
)

DATA_DIR = EXAMPLES_DIR / "data"


class ColumnsForTests(unittest.TestCase):
    def test_known_stages(self) -> None:
        self.assertEqual(columns_for("raw"), ("id", "article text"))
        self.assertEqual(columns_for("translated"), ("id", "body", "translated"))
        self.assertEqual(columns_for("summarized"), ("id", "body", "translated", "summary"))
        self.assertEqual(columns_for("labeled"), ("id", "body", "summary"))
        self.assertEqual(columns_for("finetune"), ("id", "body", "summary"))
        self.assertEqual(columns_for("predictions"), ("id", "summary"))

    def test_split_aliases(self) -> None:
        self.assertEqual(columns_for("train"), columns_for("finetune"))
        self.assertEqual(columns_for("validation"), columns_for("finetune"))
        self.assertEqual(columns_for("test"), columns_for("finetune"))

    def test_unknown_stage(self) -> None:
        with self.assertRaises(SchemaError):
            columns_for("nllb_experiment")


class ValidateHeadersTests(unittest.TestCase):
    def test_accepts_exact_order(self) -> None:
        validate_headers("raw", ["id", "article text"])

    def test_rejects_wrong_order(self) -> None:
        with self.assertRaises(SchemaError):
            validate_headers("raw", ["article text", "id"])

    def test_rejects_extra_column(self) -> None:
        with self.assertRaises(SchemaError):
            validate_headers("labeled", ["id", "body", "summary", "extra"])


class ValidateRowTests(unittest.TestCase):
    def test_complete_row(self) -> None:
        validate_row("labeled", {"id": "dn-001", "body": "tekst", "summary": "kort"})

    def test_missing_column(self) -> None:
        with self.assertRaises(SchemaError):
            validate_row("labeled", {"id": "dn-001", "body": "tekst"})

    def test_empty_column(self) -> None:
        with self.assertRaises(SchemaError):
            validate_row("labeled", {"id": "dn-001", "body": "tekst", "summary": "  "})


class DanishLetterTests(unittest.TestCase):
    def test_detects_letters(self) -> None:
        self.assertTrue(has_danish_letters("færgen åbner i København"))
        self.assertFalse(has_danish_letters("the ferry opens in Copenhagen"))


class SnapshotHeaderTests(unittest.TestCase):
    def test_committed_headers_match_contracts(self) -> None:
        mapping = {
            "raw": "raw",
            "translated": "translated",
            "summarized": "summarized",
            "labeled": "labeled",
            "train": "finetune",
            "validation": "finetune",
            "test": "finetune",
            "predictions": "predictions",
        }
        for key, stage in mapping.items():
            path = DATA_DIR / STAGE_FILES[key]
            self.assertTrue(path.is_file(), f"missing snapshot {path}")
            with path.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                validate_headers(stage, reader.fieldnames or [])
                rows = list(reader)
            self.assertGreaterEqual(len(rows), 2, f"{path.name} is too small")
            for row in rows:
                validate_row(stage, row)

    def test_stage_column_table_is_nonempty(self) -> None:
        self.assertGreaterEqual(len(STAGE_COLUMNS), 5)


if __name__ == "__main__":
    unittest.main()
