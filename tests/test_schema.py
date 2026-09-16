from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.dns_examples.schema import (
    align_id_sets,
    validate_rows,
    validate_split_partition,
)


class ValidateRowsTests(unittest.TestCase):
    def test_happy_articles(self) -> None:
        rows = [{"id": "a", "article text": "hej"}]
        report = validate_rows(rows, "articles", fieldnames=["id", "article text"])
        self.assertTrue(report.ok)

    def test_missing_column(self) -> None:
        report = validate_rows(
            [{"id": "a", "article text": "hej"}],
            "articles",
            fieldnames=["id"],
        )
        codes = [issue.code for issue in report.issues]
        self.assertIn("missing_columns", codes)

    def test_duplicate_id(self) -> None:
        rows = [
            {"id": "a", "article text": "x"},
            {"id": "a", "article text": "y"},
        ]
        report = validate_rows(rows, "articles", fieldnames=["id", "article text"])
        self.assertTrue(any(issue.code == "duplicate_id" for issue in report.issues))

    def test_empty_cell(self) -> None:
        rows = [{"id": "a", "body": "da", "summary": "   "}]
        report = validate_rows(rows, "labeled", fieldnames=["id", "body", "summary"])
        self.assertTrue(any(issue.code == "empty_cell" for issue in report.issues))

    def test_unknown_stage(self) -> None:
        with self.assertRaises(KeyError):
            validate_rows([], "not-a-stage")


class AlignAndSplitTests(unittest.TestCase):
    def test_id_mismatch(self) -> None:
        issues = align_id_sets(["a", "b"], ["a", "c"], left_name="left", right_name="right")
        self.assertEqual(len(issues), 2)

    def test_partition_ok(self) -> None:
        issues = validate_split_partition(["a", "b", "c"], ["a"], ["b"], ["c"])
        self.assertEqual(issues, [])

    def test_partition_overlap_and_gap(self) -> None:
        issues = validate_split_partition(["a", "b", "c"], ["a", "b"], ["b"], ["d"])
        codes = {issue.code for issue in issues}
        self.assertIn("split_overlap", codes)
        self.assertIn("split_unknown_id", codes)
        self.assertIn("split_incomplete", codes)


if __name__ == "__main__":
    unittest.main()
