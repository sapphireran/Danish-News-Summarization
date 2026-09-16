from __future__ import annotations

import sys
import unittest
from pathlib import Path

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))

from schema import (
    STAGE_0_ARTICLES,
    STAGE_1_TRANSLATED,
    STAGE_3_LABELED,
    STAGE_4_SPLIT,
    infer_stage_from_filename,
    missing_columns,
    required_columns,
)


class SchemaTests(unittest.TestCase):
    def test_stage_zero_requires_spaced_column(self) -> None:
        cols = required_columns(STAGE_0_ARTICLES)
        self.assertEqual(cols, ("id", "article text"))

    def test_missing_columns_lists_only_absent(self) -> None:
        missing = missing_columns(STAGE_1_TRANSLATED, ["id", "body", "extra"])
        self.assertEqual(missing, ["translated"])

    def test_unknown_stage_raises(self) -> None:
        with self.assertRaises(ValueError):
            required_columns("not-a-stage")

    def test_infer_stage_from_course_and_sample_names(self) -> None:
        cases = {
            "10000_articles_without_linebreaks.csv": STAGE_0_ARTICLES,
            "00_articles_sample.csv": STAGE_0_ARTICLES,
            "translated_articles.csv": STAGE_1_TRANSLATED,
            "summarized_file_ml80_rp5.0.csv": "summarized",
            "labeled_dataset_ml80_rp5.0.csv": STAGE_3_LABELED,
            "train_dataset.csv": STAGE_4_SPLIT,
            "04_validation_split_sample.csv": STAGE_4_SPLIT,
        }
        for name, stage in cases.items():
            self.assertEqual(infer_stage_from_filename(name), stage, name)

    def test_infer_unknown_is_none(self) -> None:
        self.assertIsNone(infer_stage_from_filename("notes.txt"))


if __name__ == "__main__":
    unittest.main()
