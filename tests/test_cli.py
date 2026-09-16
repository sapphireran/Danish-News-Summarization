import tempfile
import unittest
from pathlib import Path

from danish_news_summarization.cli import main
from danish_news_summarization.schema import validate_table
from danish_news_summarization.csv_io import read_csv


class CliTests(unittest.TestCase):
    def test_stages_exit_zero(self) -> None:
        self.assertEqual(main(["stages"]), 0)

    def test_schema_exit_zero(self) -> None:
        self.assertEqual(main(["schema", "labeled"]), 0)

    def test_chunk_unknown_id(self) -> None:
        self.assertEqual(main(["chunk", "--id", "nope"]), 2)

    def test_export_and_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            out_dir = Path(tmp) / "out"
            self.assertEqual(main(["export-data", "--out", str(data_dir)]), 0)
            self.assertEqual(main(["dry-run", "--out", str(out_dir), "--max-length", "50"]), 0)
            labeled = read_csv(out_dir / "sample_labeled_dataset.csv")
            validate_table("labeled", labeled)
            self.assertTrue((out_dir / "compression_stats.json").exists())
            self.assertTrue((data_dir / "sample_article_index.csv").exists())


if __name__ == "__main__":
    unittest.main()
