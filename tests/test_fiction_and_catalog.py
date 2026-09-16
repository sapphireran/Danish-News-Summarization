import csv
import json
import tempfile
import unittest
from pathlib import Path

from silverlab.catalog import ERROR_CODES, dump_catalog_json, items_for_article, load_catalog
from silverlab.course_csv import ARTICLE_HEADER, write_articles_csv
from silverlab.fiction import all_briefs, brief_by_id, dump_briefs_json, load_briefs
from silverlab.validate import failed_checks, run_checks


class FictionCatalogTests(unittest.TestCase):
    def test_sixteen_unique_lab_ids(self) -> None:
        briefs = all_briefs()
        ids = [brief.id for brief in briefs]
        self.assertEqual(len(briefs), 16)
        self.assertEqual(len(set(ids)), 16)
        self.assertTrue(all(item.startswith("lab-") for item in ids))

    def test_brief_by_id(self) -> None:
        brief = brief_by_id("lab-15")
        self.assertEqual(brief.topic, "natur")
        with self.assertRaises(KeyError):
            brief_by_id("dn-001")

    def test_json_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "briefs.json"
            dump_briefs_json(path)
            loaded = load_briefs(path)
            self.assertEqual(len(loaded), 16)
            self.assertEqual(loaded[0].id, "lab-01")
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(raw[0]["id"], "lab-01")

    def test_catalog_round_trip_and_codes(self) -> None:
        items = load_catalog()
        self.assertGreaterEqual(len(items), 12)
        used = {code for item in items for code in item.codes}
        self.assertTrue(used <= set(ERROR_CODES))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "errors.json"
            dump_catalog_json(path)
            again = load_catalog(path)
            self.assertEqual([item.id for item in again], [item.id for item in items])

    def test_items_for_article(self) -> None:
        hits = items_for_article("lab-01")
        self.assertGreaterEqual(len(hits), 2)
        self.assertTrue(all(item.article_id == "lab-01" for item in hits))
        self.assertEqual(items_for_article("lab-99"), [])

    def test_validate_passes(self) -> None:
        failed = failed_checks(run_checks())
        self.assertEqual(failed, [], [check.name for check in failed])

    def test_course_csv_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "articles.csv"
            write_articles_csv(path)
            with path.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                self.assertIsNotNone(reader.fieldnames)
                self.assertIn(ARTICLE_HEADER, reader.fieldnames)
                rows = list(reader)
            self.assertEqual(len(rows), 16)
            self.assertEqual(rows[0]["id"], "lab-01")
            self.assertIn("Observatorium", rows[0][ARTICLE_HEADER])
