from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.dns_examples.metrics import compression_ratio, lcs_length, rouge_l, rouge_n, word_tokens


class MetricTests(unittest.TestCase):
    def test_word_tokens_lowercases(self) -> None:
        self.assertEqual(word_tokens("Klintelund Kommune"), ["klintelund", "kommune"])

    def test_identical_rouge_is_one(self) -> None:
        text = "cykelsti mellem station og havn"
        self.assertEqual(rouge_n(text, text, 1)[2], 1.0)
        self.assertEqual(rouge_n(text, text, 2)[2], 1.0)
        self.assertEqual(rouge_l(text, text)[2], 1.0)

    def test_disjoint_rouge_is_zero(self) -> None:
        self.assertEqual(rouge_n("alpha beta", "gamma delta", 1)[2], 0.0)

    def test_partial_unigram_overlap(self) -> None:
        precision, recall, f1 = rouge_n("rød cykelsti", "ny cykelsti ved havnen", 1)
        self.assertGreater(f1, 0.0)
        self.assertLess(f1, 1.0)
        self.assertGreater(precision, 0.0)
        self.assertGreater(recall, 0.0)

    def test_lcs_length(self) -> None:
        self.assertEqual(lcs_length(["a", "b", "c"], ["a", "x", "c"]), 2)
        self.assertEqual(lcs_length([], ["a"]), 0)

    def test_compression_ratio(self) -> None:
        article = "en to tre fire fem"
        summary = "en to"
        self.assertAlmostEqual(compression_ratio(article, summary), 0.4)
        self.assertEqual(compression_ratio("", "hej"), 0.0)

    def test_empty_pair_is_perfect(self) -> None:
        self.assertEqual(rouge_n("", "", 1), (1.0, 1.0, 1.0))
        self.assertEqual(rouge_l("", ""), (1.0, 1.0, 1.0))


if __name__ == "__main__":
    unittest.main()
