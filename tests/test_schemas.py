import tempfile
import unittest
from pathlib import Path

from examples.schemas import (
    LABELED_COLUMNS,
    RAW_COLUMNS,
    SchemaError,
    infer_stage,
    validate_csv,
    validate_rows,
    validate_sample_dir,
    write_csv,
)


class ValidateRowsTests(unittest.TestCase):
    def test_accepts_clean_rows(self):
        rows = validate_rows(
            [{"id": "a", "body": "tekst", "summary": "kort"}],
            LABELED_COLUMNS,
            stage="labeled",
        )
        self.assertEqual(rows[0]["id"], "a")

    def test_rejects_missing_column(self):
        with self.assertRaises(SchemaError):
            validate_rows([{"id": "a", "body": "tekst"}], LABELED_COLUMNS)

    def test_rejects_empty_field(self):
        with self.assertRaises(SchemaError):
            validate_rows(
                [{"id": "a", "body": "tekst", "summary": "   "}],
                LABELED_COLUMNS,
            )

    def test_rejects_duplicate_id(self):
        with self.assertRaises(SchemaError):
            validate_rows(
                [
                    {"id": "a", "body": "x", "summary": "y"},
                    {"id": "a", "body": "z", "summary": "w"},
                ],
                LABELED_COLUMNS,
            )

    def test_rejects_empty_table(self):
        with self.assertRaises(SchemaError):
            validate_rows([], LABELED_COLUMNS)


class ValidateCsvTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.csv"
            write_csv(
                path,
                [{"id": "n1", "article text": "Hej verden."}],
                RAW_COLUMNS,
            )
            rows = validate_csv(path, RAW_COLUMNS, stage="raw")
            self.assertEqual(rows[0]["article text"], "Hej verden.")

    def test_unexpected_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.csv"
            write_csv(
                path,
                [{"id": "n1", "article text": "Hej.", "extra": "nope"}],
                ("id", "article text", "extra"),
            )
            with self.assertRaises(SchemaError):
                validate_csv(path, RAW_COLUMNS, stage="raw")


class SampleDirTests(unittest.TestCase):
    def test_committed_sample_dir(self):
        counts = validate_sample_dir("examples/sample_data")
        self.assertEqual(counts["00_raw_articles.csv"], 5)
        self.assertEqual(counts["04_train_dataset.csv"], 3)
        self.assertEqual(counts["04_validation_dataset.csv"], 1)
        self.assertEqual(counts["04_test_dataset.csv"], 1)

    def test_infer_stage(self):
        self.assertEqual(infer_stage("examples/sample_data/03_labeled_dataset.csv"), "labeled")
        with self.assertRaises(SchemaError):
            infer_stage("unknown.csv")


if __name__ == "__main__":
    unittest.main()
