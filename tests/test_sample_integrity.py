import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.support import REPO_ROOT

from examples.dns_examples.io import ids_of, read_csv
from examples.dns_examples.schema import (
    SCHEMAS,
    align_id_sets,
    validate_rows,
    validate_split_partition,
)
from examples.dns_examples.sentences import split_sentences

DATA = REPO_ROOT / "examples" / "data"


def _header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle))


class FixtureIntegrityTests(unittest.TestCase):
    def test_all_stage_files_exist(self) -> None:
        for name in (
            "sample_articles.csv",
            "sample_translated.csv",
            "sample_summaries_en.csv",
            "sample_labeled.csv",
            "splits/train.csv",
            "splits/validation.csv",
            "splits/test.csv",
        ):
            self.assertTrue((DATA / name).is_file(), msg=name)

    def test_headers_and_cells(self) -> None:
        mapping = {
            "articles": DATA / "sample_articles.csv",
            "translated": DATA / "sample_translated.csv",
            "summaries_en": DATA / "sample_summaries_en.csv",
            "labeled": DATA / "sample_labeled.csv",
        }
        for stage, path in mapping.items():
            rows = read_csv(path)
            report = validate_rows(rows, stage, fieldnames=_header(path))
            self.assertTrue(report.ok, msg=[str(i) for i in report.issues])
            self.assertEqual(len(rows), 10)
            self.assertEqual(tuple(_header(path)), SCHEMAS[stage])

    def test_ids_align_across_stages(self) -> None:
        articles = ids_of(read_csv(DATA / "sample_articles.csv"))
        for filename in ("sample_translated.csv", "sample_summaries_en.csv", "sample_labeled.csv"):
            other = ids_of(read_csv(DATA / filename))
            issues = align_id_sets(articles, other, left_name="articles", right_name=filename)
            self.assertEqual(issues, [], msg=filename)
            self.assertEqual(articles, other)

    def test_splits_partition_the_labeled_ids(self) -> None:
        labeled = ids_of(read_csv(DATA / "sample_labeled.csv"))
        train = ids_of(read_csv(DATA / "splits" / "train.csv"))
        validation = ids_of(read_csv(DATA / "splits" / "validation.csv"))
        test = ids_of(read_csv(DATA / "splits" / "test.csv"))
        issues = validate_split_partition(labeled, train, validation, test)
        self.assertEqual(issues, [], msg=[str(i) for i in issues])
        self.assertEqual(len(train), 6)
        self.assertEqual(len(validation), 2)
        self.assertEqual(len(test), 2)

    def test_bodies_are_stable_across_files(self) -> None:
        danish = {row["id"]: row["article text"] for row in read_csv(DATA / "sample_articles.csv")}
        for filename in ("sample_translated.csv", "sample_summaries_en.csv", "sample_labeled.csv"):
            for row in read_csv(DATA / filename):
                self.assertEqual(row["body"], danish[row["id"]], msg=f"{filename} {row['id']}")

    def test_oesterhavn_is_one_sentence(self) -> None:
        rows = {row["id"]: row["article text"] for row in read_csv(DATA / "sample_articles.csv")}
        self.assertEqual(len(split_sentences(rows["oesterhavn-kvote"])), 1)

    def test_aligned_sentence_counts_for_short_stories(self) -> None:
        translated = read_csv(DATA / "sample_translated.csv")
        for row in translated:
            if row["id"] == "oesterhavn-kvote":
                continue
            da_n = len(split_sentences(row["body"]))
            en_n = len(split_sentences(row["translated"]))
            self.assertEqual(da_n, en_n, msg=row["id"])
            self.assertGreaterEqual(da_n, 3, msg=row["id"])

    def test_summaries_are_shorter_than_articles(self) -> None:
        for row in read_csv(DATA / "sample_labeled.csv"):
            self.assertLess(len(row["summary"]), len(row["body"]), msg=row["id"])

    def test_no_real_newsroom_names_in_fixtures(self) -> None:
        banned = ("TV2 Nord", "Nordjylland", "DaNewsroom", "Ekstra Bladet", "Jyllands-Posten")
        blob = (DATA / "sample_articles.csv").read_text(encoding="utf-8")
        for name in banned:
            self.assertNotIn(name, blob)


if __name__ == "__main__":
    unittest.main()
