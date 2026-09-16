import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.support import REPO_ROOT

from examples.dns_examples.io import read_csv
from examples.dns_examples.mock_models import HopLexicon, lead_n_danish, mock_mark
from examples.dns_examples.paths import DATA_DIR
from examples.dns_examples.pipeline import load_default_lexicon, run_toy_pipeline, write_pipeline_csvs
from examples.dns_examples.schema import validate_rows


class PipelineTests(unittest.TestCase):
    def test_known_ids_reuse_fixtures(self) -> None:
        articles = read_csv(DATA_DIR / "sample_articles.csv")
        labeled = {row["id"]: row["summary"] for row in read_csv(DATA_DIR / "sample_labeled.csv")}
        english = {row["id"]: row["translated"] for row in read_csv(DATA_DIR / "sample_translated.csv")}
        result = run_toy_pipeline(articles, load_default_lexicon(), pack_budget=40)
        self.assertEqual(len(result.records), 10)
        for rec in result.records:
            self.assertEqual(rec.english, english[rec.id])
            self.assertEqual(rec.danish_summary, labeled[rec.id])
            self.assertGreaterEqual(rec.pack_count, 1)

    def test_unknown_id_is_marked(self) -> None:
        rows = [{"id": "brand-new", "article text": "En ny historie. Den er kort."}]
        result = run_toy_pipeline(rows, HopLexicon(), pack_budget=40)
        rec = result.records[0]
        self.assertTrue(rec.english.startswith("[da→en]"))
        self.assertTrue(rec.danish_summary.startswith("[en→da]"))
        self.assertIn("En ny historie", rec.english)

    def test_write_csvs_match_schema(self) -> None:
        articles = read_csv(DATA_DIR / "sample_articles.csv")[:2]
        result = run_toy_pipeline(articles, load_default_lexicon(), pack_budget=40)
        with tempfile.TemporaryDirectory() as tmp:
            written = write_pipeline_csvs(result, Path(tmp))
            self.assertEqual(set(written), {"articles", "translated", "summaries_en", "labeled"})
            mapping = {
                "articles": "articles",
                "translated": "translated",
                "summaries_en": "summaries_en",
                "labeled": "labeled",
            }
            for stage, key in mapping.items():
                rows = read_csv(written[key])
                report = validate_rows(rows, stage, fieldnames=list(rows[0].keys()) if rows else [])
                self.assertTrue(report.ok, msg=[str(i) for i in report.issues])
                self.assertEqual(len(rows), 2)

    def test_long_article_packs_more_than_one_group_on_small_budget(self) -> None:
        articles = [
            row
            for row in read_csv(DATA_DIR / "sample_articles.csv")
            if row["id"] == "oesterhavn-kvote"
        ]
        tight = run_toy_pipeline(articles, load_default_lexicon(), pack_budget=15)
        wide = run_toy_pipeline(articles, load_default_lexicon(), pack_budget=400)
        self.assertGreater(tight.records[0].pack_count, 1)
        self.assertEqual(wide.records[0].pack_count, 1)

    def test_lead_baseline_is_first_sentence(self) -> None:
        text = "Første sætning. Anden sætning."
        self.assertEqual(lead_n_danish(text, 1), "Første sætning.")
        self.assertEqual(lead_n_danish(text, 2), text)

    def test_mock_mark(self) -> None:
        self.assertEqual(mock_mark("da→en", "hej"), "[da→en] hej")

    def test_repo_root_exists(self) -> None:
        self.assertTrue((REPO_ROOT / "translate.py").is_file())


if __name__ == "__main__":
    unittest.main()
