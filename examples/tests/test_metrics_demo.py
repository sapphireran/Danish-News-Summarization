"""Toy unigram / LCS metrics, including the injected prediction errors."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXAMPLES_DIR))

from corpus import by_id  # noqa: E402
from metrics_demo import (  # noqa: E402
    compression_ratio,
    lcs_f1,
    lcs_length,
    score_corpus,
    tokenize,
    unigram_scores,
)
from schema import STAGE_FILES  # noqa: E402

DATA_DIR = EXAMPLES_DIR / "data"


class TokenizeTests(unittest.TestCase):
    def test_keeps_danish_letters(self) -> None:
        tokens = tokenize("Færgen åbner i København")
        self.assertEqual(tokens, ["færgen", "åbner", "i", "københavn"])


class UnigramTests(unittest.TestCase):
    def test_identical_is_one(self) -> None:
        p, r, f1 = unigram_scores("en kort tekst", "en kort tekst")
        self.assertEqual((p, r, f1), (1.0, 1.0, 1.0))

    def test_empty_vs_text_is_zero(self) -> None:
        self.assertEqual(unigram_scores("", "hej"), (0.0, 0.0, 0.0))

    def test_partial_overlap(self) -> None:
        _p, recall, _f1 = unigram_scores("nordhavn bibliotek", "nordhavn bibliotek åbner")
        self.assertAlmostEqual(recall, 2 / 3)


class LcsTests(unittest.TestCase):
    def test_length(self) -> None:
        self.assertEqual(lcs_length(["a", "b", "c"], ["a", "x", "c"]), 2)

    def test_identical_f1(self) -> None:
        self.assertEqual(lcs_f1("en to tre", "en to tre"), 1.0)


class CompressionTests(unittest.TestCase):
    def test_ratio(self) -> None:
        self.assertAlmostEqual(compression_ratio("abcd", "abcdefgh"), 0.5)

    def test_empty_body(self) -> None:
        self.assertEqual(compression_ratio("x", ""), 0.0)


class CorpusScoreTests(unittest.TestCase):
    def test_scores_every_example_id(self) -> None:
        rows = score_corpus(
            DATA_DIR / STAGE_FILES["labeled"],
            DATA_DIR / STAGE_FILES["predictions"],
        )
        self.assertEqual([row.id for row in rows], sorted(by_id()))

    def test_near_copy_is_almost_perfect(self) -> None:
        rows = {row.id: row for row in self._rows()}
        self.assertGreater(rows["dn-005"].unigram_f1, 0.99)

    def test_hallucination_hurts_precision(self) -> None:
        rows = {row.id: row for row in self._rows()}
        # dn-004 invents a swimming hall; precision should be below the near-copy.
        self.assertLess(rows["dn-004"].unigram_precision, rows["dn-005"].unigram_precision)

    def test_generic_rewrite_hurts_recall(self) -> None:
        rows = {row.id: row for row in self._rows()}
        self.assertLess(rows["dn-010"].unigram_recall, rows["dn-005"].unigram_recall)

    def test_dropped_number_hurts_recall(self) -> None:
        gold = by_id()["dn-001"].summary_da
        pred = by_id()["dn-001"].toy_prediction_da
        _p, recall, _f1 = unigram_scores(pred, gold)
        self.assertNotIn("21", tokenize(pred))
        self.assertIn("21", tokenize(gold))
        self.assertLess(recall, 1.0)

    def _rows(self):
        return score_corpus(
            DATA_DIR / STAGE_FILES["labeled"],
            DATA_DIR / STAGE_FILES["predictions"],
        )


if __name__ == "__main__":
    unittest.main()
