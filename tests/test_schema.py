import unittest

from danish_summarization.schema import (
    FILE_HINTS,
    LABELED_COLUMNS,
    RAW_ARTICLE_COLUMNS,
    missing_columns,
    required_columns,
    validate_frame,
)


class SchemaContractTests(unittest.TestCase):
    def test_raw_columns_match_translate_script(self):
        self.assertEqual(required_columns("raw"), ("id", "article text"))

    def test_labeled_columns_match_finetune_script(self):
        self.assertEqual(required_columns("labeled"), ("id", "body", "summary"))
        self.assertEqual(LABELED_COLUMNS, ("id", "body", "summary"))

    def test_unknown_stage_lists_known_names(self):
        with self.assertRaises(ValueError) as ctx:
            required_columns("inference")
        self.assertIn("labeled", str(ctx.exception))

    def test_missing_columns_reports_only_absences(self):
        self.assertEqual(
            missing_columns(["id", "body"], "labeled"),
            ["summary"],
        )

    def test_validate_frame_accepts_a_complete_raw_table(self):
        frame = {
            "id": ["a1", "a2"],
            "article text": ["tekst et", "tekst to"],
        }
        self.assertEqual(validate_frame(frame, "raw"), [])

    def test_validate_frame_flags_missing_and_duplicate_ids(self):
        frame = {
            "id": ["a1", "a1"],
            "body": ["x", "y"],
        }
        problems = validate_frame(frame, "labeled")
        self.assertTrue(any("summary" in problem for problem in problems))
        self.assertTrue(any("duplicate" in problem for problem in problems))

    def test_file_hints_cover_the_root_scripts(self):
        self.assertEqual(
            FILE_HINTS["raw"],
            "10000_articles_without_linebreaks.csv",
        )
        self.assertIn("nordjylland", "alexandrainst/nordjylland-news-summarization")
        self.assertTrue(RAW_ARTICLE_COLUMNS[1] == "article text")


if __name__ == "__main__":
    unittest.main()
