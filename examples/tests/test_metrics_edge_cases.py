"""Extra overlap-metric cases that are easy to get wrong."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from text_lib import overlap_f1, rouge_l_f1, score_overlap, word_tokens  # noqa: E402


class EdgeCases(unittest.TestCase):
    def test_empty_against_empty_is_perfect(self) -> None:
        scores = score_overlap("", "")
        self.assertEqual(scores.as_dict()["rouge1"], 1.0)
        self.assertEqual(scores.rouge2, 1.0)
        self.assertEqual(scores.rougeL, 1.0)

    def test_empty_against_text_is_zero(self) -> None:
        scores = score_overlap("", "cykelsti")
        self.assertEqual(scores.rouge1, 0.0)
        self.assertEqual(scores.rougeL, 0.0)

    def test_case_and_punctuation_are_normalized(self) -> None:
        left = "Hjørring åbner stien!"
        right = "hjørring åbner stien"
        scores = score_overlap(left, right)
        self.assertEqual(scores.rouge1, 1.0)

    def test_bigram_penalizes_shuffled_unigrams(self) -> None:
        left = "ny cykelsti i hjørring"
        right = "hjørring i cykelsti ny"
        r1 = overlap_f1(word_tokens(left), word_tokens(right), 1)
        r2 = overlap_f1(word_tokens(left), word_tokens(right), 2)
        self.assertGreater(r1, 0.9)
        self.assertLess(r2, 0.2)

    def test_rouge_l_rewards_shared_order(self) -> None:
        pred = word_tokens("a b c d")
        gold = word_tokens("a x b y c")
        self.assertGreater(rouge_l_f1(pred, gold), 0.5)


if __name__ == "__main__":
    unittest.main()
