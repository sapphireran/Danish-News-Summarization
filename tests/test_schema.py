import unittest

from danish_news_summarization.schema import (
    STAGE_COLUMNS,
    SchemaError,
    describe_stage,
    project_row,
    validate_row,
    validate_table,
)


class SchemaTests(unittest.TestCase):
    def test_known_stages(self) -> None:
        self.assertEqual(STAGE_COLUMNS["raw_articles"], ["id", "article text"])
        self.assertEqual(STAGE_COLUMNS["labeled"], ["id", "body", "summary"])

    def test_validate_row_accepts_complete_row(self) -> None:
        validate_row("labeled", {"id": "dn-001", "body": "tekst", "summary": "kort"})

    def test_missing_column(self) -> None:
        with self.assertRaises(SchemaError) as ctx:
            validate_row("translated", {"id": "x", "body": "y"})
        self.assertIn("translated", str(ctx.exception))

    def test_empty_value(self) -> None:
        with self.assertRaises(SchemaError):
            validate_row("labeled", {"id": "x", "body": "y", "summary": "  "})

    def test_unknown_stage(self) -> None:
        with self.assertRaises(SchemaError):
            validate_row("not-a-stage", {"id": "x"})

    def test_empty_table(self) -> None:
        with self.assertRaises(SchemaError):
            validate_table("labeled", [])

    def test_project_row_strips_extras(self) -> None:
        row = project_row(
            "labeled",
            {"id": "1", "body": "b", "summary": "s", "translated": "drop me"},
        )
        self.assertEqual(row, {"id": "1", "body": "b", "summary": "s"})

    def test_describe_stage_lists_columns(self) -> None:
        text = describe_stage("summarized")
        self.assertIn("translated", text)
        self.assertIn("summary", text)


if __name__ == "__main__":
    unittest.main()
