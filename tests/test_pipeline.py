import json
import tempfile
import unittest
from pathlib import Path

from danish_news_summarization.csv_io import read_csv, write_csv
from danish_news_summarization.pipeline import identity_translate, lead_sentence_summary, run_dry_pipeline
from danish_news_summarization.sample_data import SAMPLE_ARTICLES, articles_by_topic, get_article, list_topics
from danish_news_summarization.schema import STAGE_COLUMNS, validate_table


class SampleDataTests(unittest.TestCase):
    def test_ten_articles_with_unique_ids(self) -> None:
        ids = [article.id for article in SAMPLE_ARTICLES]
        self.assertEqual(len(ids), 10)
        self.assertEqual(len(set(ids)), 10)

    def test_every_article_has_aligned_fields(self) -> None:
        for article in SAMPLE_ARTICLES:
            self.assertGreater(len(article.body.split()), 40)
            self.assertGreater(len(article.translation.split()), 40)
            self.assertGreater(len(article.danish_summary.split()), 8)
            self.assertGreater(len(article.english_summary.split()), 8)
            self.assertTrue(article.id.startswith("dn-"))

    def test_lookup_helpers(self) -> None:
        self.assertIn("energi", list_topics())
        self.assertEqual(get_article("dn-002").city, "Hirtshals")
        self.assertEqual(len(articles_by_topic("trafik")), 1)
        with self.assertRaises(KeyError):
            get_article("dn-999")


class DryRunTests(unittest.TestCase):
    def test_reference_labels_preserve_handwritten_summaries(self) -> None:
        report = run_dry_pipeline(SAMPLE_ARTICLES[:3], text_max_length=60)
        tables = report.tables()
        for stage in ("raw_articles", "translated", "summarized", "labeled"):
            validate_table(stage, tables[stage])
        self.assertEqual(tables["labeled"][0]["summary"], SAMPLE_ARTICLES[0].danish_summary)
        self.assertEqual(tables["summarized"][0]["summary"], SAMPLE_ARTICLES[0].english_summary)

    def test_stub_mode_marks_translation_direction(self) -> None:
        report = run_dry_pipeline(SAMPLE_ARTICLES[:1], use_reference_labels=False, text_max_length=50)
        self.assertIn("[da→en]", report.records[0].translated)
        self.assertIn("[en→da]", report.records[0].danish_summary)

    def test_compression_rows_have_ratios(self) -> None:
        report = run_dry_pipeline(SAMPLE_ARTICLES, text_max_length=80)
        rows = report.compression_rows()
        self.assertEqual(len(rows), 10)
        for row in rows:
            self.assertGreater(row["danish_words"], row["danish_summary_words"])
            self.assertGreater(row["translation_windows"], 0)


class StubHelperTests(unittest.TestCase):
    def test_identity_translate_prefix(self) -> None:
        self.assertEqual(identity_translate("hej", "da→en"), "[da→en] hej")

    def test_lead_sentence_summary(self) -> None:
        text = "Første sætning. Anden sætning. Tredje sætning."
        self.assertEqual(lead_sentence_summary(text, max_sentences=2), "Første sætning. Anden sætning.")


class CsvRoundTripTests(unittest.TestCase):
    def test_write_and_read_labeled(self) -> None:
        rows = [article.labeled_row for article in SAMPLE_ARTICLES]
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(Path(tmp) / "labeled.csv", rows, STAGE_COLUMNS["labeled"])
            loaded = read_csv(path)
        validate_table("labeled", loaded)
        self.assertEqual(loaded[0]["id"], "dn-001")


class JsonStatsSmokeTests(unittest.TestCase):
    def test_stats_are_json_serialisable(self) -> None:
        report = run_dry_pipeline(SAMPLE_ARTICLES[:2])
        payload = json.dumps(report.compression_rows())
        self.assertIn("dn-001", payload)


if __name__ == "__main__":
    unittest.main()
