import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from examples.demo_pipeline import main, split_labeled_rows, stable_bucket
from examples.inspect_sample import main as inspect_main
from examples.schemas import LABELED_COLUMNS, validate_csv


SAMPLE = Path("examples/sample_data")


class HashSplitTests(unittest.TestCase):
    def test_stable_bucket_is_deterministic(self):
        self.assertEqual(stable_bucket("aalborg-library-hours"), stable_bucket("aalborg-library-hours"))
        self.assertGreaterEqual(stable_bucket("x"), 0.0)
        self.assertLess(stable_bucket("x"), 1.0)

    def test_known_ids_land_in_documented_splits(self):
        labeled = validate_csv(SAMPLE / "03_labeled_dataset.csv", LABELED_COLUMNS, stage="labeled")
        train, validation, test = split_labeled_rows(labeled)
        self.assertEqual(
            [row["id"] for row in train],
            ["aalborg-library-hours", "hjoerring-wind-meeting", "frederikshavn-school-wing"],
        )
        self.assertEqual([row["id"] for row in validation], ["viborg-museum-sunday"])
        self.assertEqual([row["id"] for row in test], ["skagen-harbor-festival"])

    def test_committed_split_files_match_hash(self):
        labeled = validate_csv(SAMPLE / "03_labeled_dataset.csv", LABELED_COLUMNS, stage="labeled")
        train, validation, test = split_labeled_rows(labeled)
        on_disk_train = validate_csv(SAMPLE / "04_train_dataset.csv", LABELED_COLUMNS, stage="train")
        on_disk_val = validate_csv(SAMPLE / "04_validation_dataset.csv", LABELED_COLUMNS, stage="val")
        on_disk_test = validate_csv(SAMPLE / "04_test_dataset.csv", LABELED_COLUMNS, stage="test")
        self.assertEqual([row["id"] for row in on_disk_train], [row["id"] for row in train])
        self.assertEqual([row["id"] for row in on_disk_val], [row["id"] for row in validation])
        self.assertEqual([row["id"] for row in on_disk_test], [row["id"] for row in test])


class DemoCliTests(unittest.TestCase):
    def test_demo_exits_zero(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main([])
        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("Validated sample CSVs", output)
        self.assertIn("aalborg-library-hours", output)
        self.assertIn("without loading translation", output)

    def test_inspect_list_ids(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = inspect_main(["--list-ids"])
        self.assertEqual(code, 0)
        self.assertIn("skagen-harbor-festival", buffer.getvalue())

    def test_inspect_article(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = inspect_main(["--article-id", "skagen-harbor-festival"])
        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("Raw Danish", output)
        self.assertIn("Danish silver summary", output)
        self.assertIn("Havnefest", output)

    def test_inspect_unknown_id(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = inspect_main(["--article-id", "does-not-exist"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
