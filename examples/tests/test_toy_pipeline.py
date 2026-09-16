"""End-to-end checks for the example snapshots and exporter."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXAMPLES_DIR))

from corpus import ARTICLES, articles_for_split, ids  # noqa: E402
from export_sample_csvs import export_all  # noqa: E402
from schema import STAGE_FILES, has_danish_letters  # noqa: E402
from toy_pipeline import DEMO_BUDGET, format_human, run_report  # noqa: E402

DATA_DIR = EXAMPLES_DIR / "data"


class CorpusTests(unittest.TestCase):
    def test_ten_articles_stable_ids(self) -> None:
        self.assertEqual(len(ARTICLES), 10)
        self.assertEqual(ids(), [f"dn-{index:03d}" for index in range(1, 11)])

    def test_split_counts(self) -> None:
        self.assertEqual(len(articles_for_split("train")), 6)
        self.assertEqual(len(articles_for_split("validation")), 2)
        self.assertEqual(len(articles_for_split("test")), 2)

    def test_every_article_has_danish_and_english(self) -> None:
        for article in ARTICLES:
            self.assertTrue(has_danish_letters(article.body_da), article.id)
            self.assertTrue(has_danish_letters(article.summary_da), article.id)
            self.assertIn(" ", article.body_en)
            self.assertTrue(article.summary_en)
            self.assertTrue(article.toy_prediction_da)


class ExporterTests(unittest.TestCase):
    def test_export_matches_committed_ids_and_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            paths = export_all(out)
            self.assertEqual(len(paths), 8)
            for key, filename in STAGE_FILES.items():
                generated = out / filename
                committed = DATA_DIR / filename
                self.assertTrue(generated.is_file(), filename)
                self.assertTrue(committed.is_file(), filename)
                with generated.open(encoding="utf-8", newline="") as handle:
                    gen_reader = csv.DictReader(handle)
                    gen_fields = gen_reader.fieldnames
                    gen_rows = list(gen_reader)
                with committed.open(encoding="utf-8", newline="") as handle:
                    com_reader = csv.DictReader(handle)
                    com_fields = com_reader.fieldnames
                    com_rows = list(com_reader)
                self.assertEqual(gen_fields, com_fields, filename)
                self.assertEqual(
                    [row["id"] for row in gen_rows],
                    [row["id"] for row in com_rows],
                    filename,
                )

    def test_committed_export_roundtrip_bodies(self) -> None:
        """Re-export into a temp dir and compare full labeled summaries."""
        with tempfile.TemporaryDirectory() as tmp:
            export_all(Path(tmp))
            generated = Path(tmp) / STAGE_FILES["labeled"]
            committed = DATA_DIR / STAGE_FILES["labeled"]
            with generated.open(encoding="utf-8", newline="") as handle:
                gen = {row["id"]: row["summary"] for row in csv.DictReader(handle)}
            with committed.open(encoding="utf-8", newline="") as handle:
                com = {row["id"]: row["summary"] for row in csv.DictReader(handle)}
            self.assertEqual(gen, com)


class PipelineReportTests(unittest.TestCase):
    def test_report_on_committed_data(self) -> None:
        report = run_report(DATA_DIR, DEMO_BUDGET)
        self.assertEqual(report["n_articles"], 10)
        harbor = next(item for item in report["chunk_reports"] if item["id"] == "dn-006")
        self.assertGreaterEqual(harbor["n_chunks"], 2)
        human = format_human(report)
        self.assertIn("dn-006", human)
        self.assertIn("All stage schemas and id alignments checked out.", human)

    def test_json_is_serializable(self) -> None:
        report = run_report(DATA_DIR, DEMO_BUDGET)
        payload = json.dumps(report, ensure_ascii=False)
        self.assertIn("Frederikshavn", payload)

    def test_report_on_fresh_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            export_all(Path(tmp))
            report = run_report(Path(tmp), DEMO_BUDGET)
            self.assertEqual(report["splits"]["test"], ["dn-007", "dn-010"])


if __name__ == "__main__":
    unittest.main()
