import csv
import subprocess
import sys
import unittest
from pathlib import Path

from danish_summarization.schema import validate_frame

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


def _rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _frame(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    return {key: [row[key] for row in rows] for key in rows[0]}


class SampleDataTests(unittest.TestCase):
    def test_every_stage_file_exists(self):
        for name in (
            "sample_articles.csv",
            "sample_translated.csv",
            "sample_summarized.csv",
            "sample_labeled.csv",
            "sample_train.csv",
        ):
            self.assertTrue((DATA / name).is_file(), name)

    def test_stage_contracts(self):
        checks = (
            ("sample_articles.csv", "raw"),
            ("sample_translated.csv", "translated"),
            ("sample_summarized.csv", "summarized"),
            ("sample_labeled.csv", "labeled"),
            ("sample_train.csv", "train"),
        )
        for name, stage in checks:
            problems = validate_frame(_frame(_rows(name)), stage)
            self.assertEqual(problems, [], f"{name}: {problems}")

    def test_ids_are_stable_across_labeling_stages(self):
        raw_ids = [row["id"] for row in _rows("sample_articles.csv")]
        self.assertEqual(len(raw_ids), 6)
        self.assertTrue(all(item.startswith("sample-") for item in raw_ids))
        for name in (
            "sample_translated.csv",
            "sample_summarized.csv",
            "sample_labeled.csv",
        ):
            self.assertEqual([row["id"] for row in _rows(name)], raw_ids, name)

    def test_train_split_is_a_subset(self):
        labeled_ids = {row["id"] for row in _rows("sample_labeled.csv")}
        train_ids = [row["id"] for row in _rows("sample_train.csv")]
        self.assertEqual(train_ids, ["sample-001", "sample-004"])
        self.assertTrue(set(train_ids).issubset(labeled_ids))

    def test_bodies_are_non_empty_danish_looking_text(self):
        for row in _rows("sample_articles.csv"):
            body = row["article text"]
            self.assertGreater(len(body.split()), 40, row["id"])
            self.assertIn(".", body)


class ExampleScriptTests(unittest.TestCase):
    def _run(self, script: str, extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(ROOT / "examples" / script)]
        if extra:
            command.extend(extra)
        return subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_inspect_script_accepts_all_sample_tables(self):
        result = self._run("inspect_csv_schema.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("All example tables match", result.stdout)

    def test_chunk_script_prints_windows(self):
        result = self._run("chunk_sample_articles.py", ["--max-length", "40"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("sample-001", result.stdout)
        self.assertIn("window", result.stdout)

    def test_pipeline_walkthrough_keeps_ids(self):
        result = self._run("simulate_labeling_pipeline.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("6 articles kept their ids", result.stdout)

    def test_recipe_script_mentions_mt5_and_caveats(self):
        result = self._run("print_training_recipe.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("google/mt5-large", result.stdout)
        self.assertIn("Ctranslate_converter.py", result.stdout)
        self.assertIn("./small_model", result.stdout)


if __name__ == "__main__":
    unittest.main()
