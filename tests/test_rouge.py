import unittest

from silverlab.rouge import lcs_length, mean_scores, rouge_l, rouge_n, score_pair


class RougeTests(unittest.TestCase):
    def test_identical_is_one(self) -> None:
        text = "Katten sidder i vinduet."
        for n in (1, 2):
            score = rouge_n(text, text, n=n)
            self.assertAlmostEqual(score.precision, 1.0)
            self.assertAlmostEqual(score.recall, 1.0)
            self.assertAlmostEqual(score.fmeasure, 1.0)
        score = rouge_l(text, text)
        self.assertAlmostEqual(score.fmeasure, 1.0)

    def test_partial_unigram_overlap(self) -> None:
        score = rouge_n("katten sidder", "katten sover", n=1)
        self.assertGreater(score.fmeasure, 0.0)
        self.assertLess(score.fmeasure, 1.0)
        self.assertAlmostEqual(score.precision, 0.5)
        self.assertAlmostEqual(score.recall, 0.5)

    def test_empty_is_zero(self) -> None:
        self.assertEqual(rouge_n("", "katten").fmeasure, 0.0)
        self.assertEqual(rouge_l("katten", "").fmeasure, 0.0)

    def test_rejects_bad_n(self) -> None:
        with self.assertRaises(ValueError):
            rouge_n("a", "a", n=0)

    def test_lcs_length(self) -> None:
        self.assertEqual(lcs_length(["a", "b", "c"], ["a", "c"]), 2)
        self.assertEqual(lcs_length([], ["a"]), 0)
        self.assertEqual(lcs_length(["x"], ["y"]), 0)

    def test_score_pair_keys(self) -> None:
        metrics = score_pair("katten sidder i solen", "katten sover i solen")
        for prefix in ("rouge1", "rouge2", "rougeL"):
            for suffix in ("precision", "recall", "fmeasure"):
                self.assertIn(f"{prefix}_{suffix}", metrics)

    def test_mean_scores(self) -> None:
        rows = [
            {"rouge1_fmeasure": 0.2, "rouge2_fmeasure": 0.0},
            {"rouge1_fmeasure": 0.6, "rouge2_fmeasure": 0.4},
        ]
        means = mean_scores(rows)
        self.assertAlmostEqual(means["rouge1_fmeasure"], 0.4)
        self.assertAlmostEqual(means["rouge2_fmeasure"], 0.2)
        self.assertEqual(mean_scores([]), {})

    def test_case_and_danish_letters_match(self) -> None:
        score = rouge_n("Æblekage på Åen", "æblekage på åen", n=1)
        self.assertAlmostEqual(score.fmeasure, 1.0)
