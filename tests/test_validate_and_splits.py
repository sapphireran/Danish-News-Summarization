from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
SAMPLE_DATA = _EXAMPLES / "sample_data"
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))

from csv_util import write_rows
from schema import REQUIRED_COLUMNS, STAGE_0_ARTICLES, STAGE_3_LABELED
from split_labeled_dataset import split_rows, write_splits
from validate_csvs import (
    collect_sample_dir,
    validate_alignment,
    validate_file,
    validate_splits,
)


class SampleDataValidationTests(unittest.TestCase):
    def test_each_committed_sample_file_is_clean(self) -> None:
        staged, splits = collect_sample_dir(SAMPLE_DATA)
        self.assertGreaterEqual(len(staged), 4)
        self.assertEqual(len(splits), 3)
        issues = []
        for stage, path in staged.items():
            issues.extend(validate_file(path, stage))
        issues.extend(validate_alignment(staged))
        issues.extend(validate_splits(splits))
        self.assertEqual(issues, [], msg="\n".join(str(issue) for issue in issues))

    def test_missing_column_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            write_rows(path, ["id"], [{"id": "dn-001"}])
            issues = validate_file(path, STAGE_3_LABELED)
            kinds = {issue.kind for issue in issues}
            self.assertIn("columns", kinds)

    def test_duplicate_id_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.csv"
            write_rows(
                path,
                REQUIRED_COLUMNS[STAGE_3_LABELED],
                [
                    {"id": "dn-001", "body": "a", "summary": "b"},
                    {"id": "dn-001", "body": "c", "summary": "d"},
                ],
            )
            issues = validate_file(path, STAGE_3_LABELED)
            self.assertTrue(any(issue.kind == "duplicate_id" for issue in issues))

    def test_body_drift_between_stages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage0 = root / "00.csv"
            labeled = root / "03.csv"
            write_rows(
                stage0,
                REQUIRED_COLUMNS[STAGE_0_ARTICLES],
                [{"id": "dn-001", "article text": "original dansk"}],
            )
            write_rows(
                labeled,
                REQUIRED_COLUMNS[STAGE_3_LABELED],
                [{"id": "dn-001", "body": "ændret dansk", "summary": "kort"}],
            )
            issues = validate_alignment(
                {STAGE_0_ARTICLES: stage0, STAGE_3_LABELED: labeled}
            )
            self.assertTrue(any(issue.kind == "body_drift" for issue in issues))


class SplitTests(unittest.TestCase):
    def test_split_is_deterministic(self) -> None:
        rows = [
            {"id": f"dn-{index:03}", "body": "b", "summary": "s"}
            for index in range(1, 11)
        ]
        first = split_rows(rows, train_ratio=0.7, val_ratio=0.1, seed=2023)
        second = split_rows(rows, train_ratio=0.7, val_ratio=0.1, seed=2023)
        self.assertEqual([row["id"] for row in first["train"]], [row["id"] for row in second["train"]])
        self.assertEqual([row["id"] for row in first["test"]], [row["id"] for row in second["test"]])

    def test_split_has_no_id_overlap(self) -> None:
        rows = [
            {"id": f"dn-{index:03}", "body": "b", "summary": "s"}
            for index in range(1, 13)
        ]
        parts = split_rows(rows, train_ratio=8 / 12, val_ratio=2 / 12, seed=2023)
        train = {row["id"] for row in parts["train"]}
        val = {row["id"] for row in parts["validation"]}
        test = {row["id"] for row in parts["test"]}
        self.assertEqual(len(train | val | test), 12)
        self.assertFalse(train & val)
        self.assertFalse(train & test)
        self.assertFalse(val & test)
        self.assertEqual(len(parts["train"]), 8)
        self.assertEqual(len(parts["validation"]), 2)
        self.assertEqual(len(parts["test"]), 2)

    def test_write_splits_finetune_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "labeled.csv"
            write_rows(
                source,
                REQUIRED_COLUMNS[STAGE_3_LABELED],
                [
                    {"id": f"dn-{index:03}", "body": f"body {index}", "summary": f"sum {index}"}
                    for index in range(1, 11)
                ],
            )
            written = write_splits(
                input_path=source,
                output_dir=Path(tmp) / "out",
                train_ratio=0.7,
                val_ratio=0.1,
                seed=1,
                sample_names=False,
            )
            self.assertTrue(written["train"].name.endswith("train_dataset.csv"))
            issues = validate_splits(written)
            self.assertEqual(issues, [], msg="\n".join(str(issue) for issue in issues))

    def test_bad_ratios_raise(self) -> None:
        rows = [{"id": "a", "body": "b", "summary": "s"}]
        with self.assertRaises(ValueError):
            split_rows(rows, train_ratio=0.9, val_ratio=0.2, seed=1)


if __name__ == "__main__":
    unittest.main()
