import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.compare_summaries import compare, unigram_f1
from examples.sample_catalog import SAMPLES
from examples.schema import PIPELINE_SCHEMAS, validate_records
from examples.schema_check import check_file, default_example_jobs
from examples.toy_pipeline import run_pipeline
from examples.write_sample_csvs import COLUMNS, build_rows


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA = REPO_ROOT / "examples" / "data"


class SchemaTests(unittest.TestCase):
    def test_missing_column(self):
        problems = validate_records([{"id": "1"}], "labeled_danish")
        self.assertTrue(any("missing columns" in item for item in problems))

    def test_empty_value(self):
        problems = validate_records(
            [{"id": "1", "body": "tekst", "summary": "   "}],
            "labeled_danish",
        )
        self.assertTrue(any("empty" in item for item in problems))

    def test_unknown_stage(self):
        with self.assertRaises(KeyError):
            validate_records([], "no-such-stage")

    def test_empty_file(self):
        problems = validate_records([], "raw_articles")
        self.assertEqual(problems, ["raw_articles: file has no data rows"])


class CatalogRoundTripTests(unittest.TestCase):
    def test_built_rows_match_schemas(self):
        tables = build_rows()
        expected_counts = {
            "sample_articles.csv": 6,
            "sample_translated.csv": 6,
            "sample_summarized.csv": 6,
            "sample_labeled.csv": 6,
            "sample_finetune_train.csv": 4,
            "sample_finetune_validation.csv": 1,
            "sample_finetune_test.csv": 1,
        }
        for filename, rows in tables.items():
            self.assertEqual(list(rows[0].keys()), COLUMNS[filename])
            self.assertEqual(len(rows), expected_counts[filename])

    def test_committed_example_csvs(self):
        jobs = default_example_jobs(REPO_ROOT)
        self.assertEqual(len(jobs), 7)
        for stage, path in jobs:
            problems = check_file(path, stage)
            self.assertEqual(problems, [], msg=f"{stage} {path}: {problems}")

    def test_catalog_ids_are_unique(self):
        ids = [row["id"] for row in SAMPLES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(row["body_da"] and row["summary_da"] for row in SAMPLES))


class ToyPipelineTests(unittest.TestCase):
    def test_writes_stage_files_and_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            report = run_pipeline(
                max_batch_words=40,
                max_summary_sentences=2,
                max_summary_chars=320,
                output_dir=output,
            )
            self.assertEqual(report["articles"], 6)
            expected = {
                "translated_articles.csv",
                "summarized_file_ml80_rp5.0.csv",
                "labeled_dataset_ml80_rp5.0.csv",
                "train_dataset.csv",
                "validation_dataset.csv",
                "test_dataset.csv",
                "toy_pipeline_report.json",
            }
            self.assertTrue(expected.issubset({path.name for path in output.iterdir()}))

            with (output / "labeled_dataset_ml80_rp5.0.csv").open(newline="", encoding="utf-8") as handle:
                labeled = list(csv.DictReader(handle))
            self.assertEqual(len(labeled), 6)
            self.assertTrue(all(row["summary"].strip() for row in labeled))
            self.assertGreaterEqual(report["batches_per_article"]["ex-006-havn"], 3)

            with (output / "train_dataset.csv").open(newline="", encoding="utf-8") as handle:
                train_ids = {row["id"] for row in csv.DictReader(handle)}
            self.assertIn("ex-006-havn", train_ids)
            self.assertNotIn("ex-005-cykelsti", train_ids)


class CompareSummariesTests(unittest.TestCase):
    def test_identical_texts_score_one(self):
        scores = unigram_f1("Klitvig Havn renoverer kajen.", "Klitvig Havn renoverer kajen.")
        self.assertEqual(scores["f1"], 1.0)

    def test_disjoint_texts_score_zero(self):
        scores = unigram_f1("cykelsti skole", "hummerfestival sluse")
        self.assertEqual(scores["f1"], 0.0)

    def test_gold_versus_extractive_runs(self):
        report = compare(
            gold_path=DATA / "sample_labeled.csv",
            silver_path=None,
            max_sentences=2,
            max_chars=320,
        )
        self.assertEqual(report["n"], 6)
        self.assertGreaterEqual(report["mean_content_f1"], 0.0)
        self.assertLessEqual(report["mean_content_f1"], 1.0)


class ConfigPresenceTests(unittest.TestCase):
    def test_example_configs_exist(self):
        config_dir = REPO_ROOT / "examples" / "configs"
        self.assertTrue((config_dir / "pipeline.example.json").is_file())
        self.assertTrue((config_dir / "training.example.json").is_file())
        self.assertIn("raw_articles", PIPELINE_SCHEMAS)


if __name__ == "__main__":
    unittest.main()
