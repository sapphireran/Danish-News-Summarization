"""Unit tests for examples/scripts/text_lib.py."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from text_lib import (  # noqa: E402
    DATA_DIR,
    inspect_rows,
    lead_n_sentences,
    load_expected_columns,
    looks_like_danish,
    lcs_length,
    pack_sentences,
    read_csv,
    score_overlap,
    split_long_sentence,
    split_rows,
    split_sentences,
)


class SentenceTests(unittest.TestCase):
    def test_split_sentences_keeps_danish_period_boundaries(self) -> None:
        text = "Hjørring åbner en sti. Borgmesteren talte. Folk klappede."
        self.assertEqual(len(split_sentences(text)), 3)

    def test_lead_n_empty_and_clip(self) -> None:
        self.assertEqual(lead_n_sentences("", 2), "")
        self.assertEqual(lead_n_sentences("Kun én sætning.", 5), "Kun én sætning.")

    def test_looks_like_danish_on_fixture_lede(self) -> None:
        rows = read_csv(DATA_DIR / "sample_articles.csv")
        self.assertTrue(looks_like_danish(rows[0]["article text"]))
        self.assertFalse(looks_like_danish("The quick brown fox jumps over the lazy dog."))


class PackingTests(unittest.TestCase):
    def test_pack_sentences_respects_budget(self) -> None:
        article = " ".join(f"Dette er sætning nummer {i}." for i in range(1, 12))
        windows = pack_sentences(article, text_max_length=20, split_overlong=True)
        self.assertGreaterEqual(len(windows), 2)
        for window in windows:
            self.assertLessEqual(window.token_count, 20 + 2)  # last sentence may sit alone
            self.assertTrue(window.sentences)

    def test_overlong_sentence_is_carved(self) -> None:
        long = "ord, " * 40 + "slut."
        chunks = split_long_sentence(long, max_length=25)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunks))

    def test_empty_article_has_no_windows(self) -> None:
        self.assertEqual(pack_sentences("   ", 40), [])


class MetricTests(unittest.TestCase):
    def test_self_overlap_is_perfect(self) -> None:
        text = "Hjørring åbner en fire kilometer belyst cykelsti til stationen."
        scores = score_overlap(text, text)
        self.assertEqual(scores.rouge1, 1.0)
        self.assertEqual(scores.rouge2, 1.0)
        self.assertEqual(scores.rougeL, 1.0)

    def test_unrelated_text_is_near_zero(self) -> None:
        scores = score_overlap("cykelsti asketræer", "færge gearbox")
        self.assertLess(scores.rouge1, 0.2)

    def test_lcs_length(self) -> None:
        self.assertEqual(lcs_length(["a", "b", "c"], ["a", "x", "c"]), 2)
        self.assertEqual(lcs_length([], ["a"]), 0)

    def test_fixture_labeled_self_score(self) -> None:
        rows = read_csv(DATA_DIR / "sample_labeled.csv")
        for row in rows:
            scores = score_overlap(row["summary"], row["summary"])
            self.assertEqual(scores.rouge1, 1.0)


class SplitTests(unittest.TestCase):
    def test_split_is_deterministic_and_disjoint(self) -> None:
        rows = read_csv(DATA_DIR / "sample_labeled.csv")
        first = split_rows(rows, train=0.7, validation=0.2, test=0.1, seed=2023)
        second = split_rows(rows, train=0.7, validation=0.2, test=0.1, seed=2023)
        self.assertEqual([row["id"] for row in first["train"]], [row["id"] for row in second["train"]])
        ids = {name: {row["id"] for row in bucket} for name, bucket in first.items()}
        self.assertFalse(ids["train"] & ids["validation"])
        self.assertFalse(ids["train"] & ids["test"])
        self.assertFalse(ids["validation"] & ids["test"])
        self.assertEqual(sum(len(bucket) for bucket in first.values()), len(rows))

    def test_bad_ratios_raise(self) -> None:
        rows = read_csv(DATA_DIR / "sample_labeled.csv")
        with self.assertRaises(ValueError):
            split_rows(rows, train=0.5, validation=0.5, test=0.5, seed=1)


class ContractTests(unittest.TestCase):
    def test_fixtures_match_contracts(self) -> None:
        contracts = load_expected_columns()
        mapping = {
            "source": DATA_DIR / "sample_articles.csv",
            "translated": DATA_DIR / "sample_translated.csv",
            "summarized": DATA_DIR / "sample_summarized.csv",
            "labeled": DATA_DIR / "sample_labeled.csv",
            "nordjylland": DATA_DIR / "sample_nordjylland_mini.csv",
        }
        for stage, path in mapping.items():
            rows = read_csv(path)
            report = inspect_rows(rows, stage, path, contracts["stages"][stage])
            self.assertTrue(report.ok, msg=report.as_dict())
            self.assertGreaterEqual(report.rows, 5)


if __name__ == "__main__":
    unittest.main()
