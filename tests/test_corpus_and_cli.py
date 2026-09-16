import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from maalestok.cli import main
from maalestok.corpus import ARTICLES
from maalestok.fixtures import write_all
from maalestok.ledger import build_corpus_ledger
from maalestok.schemas import check_headers
from maalestok.validate import run_checks, summary


class CorpusTests(unittest.TestCase):
    def test_sixteen_unique(self) -> None:
        ids = [article.id for article in ARTICLES]
        self.assertEqual(len(ids), 16)
        self.assertEqual(len(set(ids)), 16)

    def test_oracle_beats_silver_on_mean(self) -> None:
        ledger = build_corpus_ledger(ARTICLES)
        self.assertGreater(ledger.mean_survival("oracle_da"), ledger.mean_survival("silver_da"))
        self.assertGreater(ledger.mean_survival("lead2_da"), ledger.mean_survival("silver_da"))

    def test_every_brief_plants_something(self) -> None:
        for article in ARTICLES:
            self.assertGreaterEqual(len(article.planted), 1, article.id)
            for err in article.planted:
                self.assertIn(err.source_raw, article.body_da, article.id)
                self.assertIn(err.silver_raw, article.silver_da, article.id)


class SchemaTests(unittest.TestCase):
    def test_raw_header(self) -> None:
        self.assertEqual(check_headers("raw", ["id", "article text"]), [])
        self.assertTrue(check_headers("raw", ["id", "body"]))

    def test_fixtures_roundtrip(self) -> None:
        with TemporaryDirectory() as tmp:
            written = write_all(Path(tmp))
            with written["raw"].open(encoding="utf-8") as handle:
                self.assertEqual(len(handle.readlines()), 17)


class ValidateAndCliTests(unittest.TestCase):
    def test_validator_all_green_after_fixtures(self) -> None:
        with TemporaryDirectory() as tmp:
            write_all(Path(tmp))
            # Validator reads the committed DATA_DIR; the in-memory corpus
            # checks must pass regardless of that directory.
            checks = [c for c in run_checks() if not c.name.startswith("csv_")]
            ok, total = summary(checks)
            failed = [c.name for c in checks if not c.ok]
            self.assertEqual(failed, [], failed)
            self.assertEqual(ok, total)

    def test_cli_list_and_ledger(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(main(["list"]), 0)
        out = buf.getvalue()
        self.assertIn("bh-01", out)
        self.assertIn("bh-16", out)

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(main(["ledger"]), 0)
        self.assertIn("mean", buf.getvalue())

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(main(["show", "bh-06"]), 0)
        self.assertIn("−8,3", buf.getvalue())

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(main(["scar"]), 0)
        self.assertIn("number_leads_the_summary", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
