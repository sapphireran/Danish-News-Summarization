import io
import unittest
from contextlib import redirect_stdout

from examples.rouge_toy import main, ngrams, rouge_n, tokenize


class TokenizeTests(unittest.TestCase):
    def test_keeps_danish_letters(self):
        tokens = tokenize("Hjørring åbner søndag.")
        self.assertIn("hjørring", tokens)
        self.assertIn("åbner", tokens)
        self.assertIn("søndag", tokens)

    def test_ngrams(self):
        self.assertEqual(ngrams(["a", "b", "c"], 2), [("a", "b"), ("b", "c")])
        self.assertEqual(ngrams(["a"], 2), [])
        with self.assertRaises(ValueError):
            ngrams(["a"], 0)


class RougeNTests(unittest.TestCase):
    def test_identity(self):
        text = "Aalborgs hovedbibliotek ændrer åbningstiderne."
        scores = rouge_n(text, text, 1)
        self.assertEqual(scores["precision"], 1.0)
        self.assertEqual(scores["recall"], 1.0)
        self.assertEqual(scores["f1"], 1.0)
        self.assertEqual(rouge_n(text, text, 2)["f1"], 1.0)

    def test_unrelated_english_vs_danish(self):
        scores = rouge_n("The weather in Lisbon is mild this week.", "Hjørring holder borgermøde.", 2)
        self.assertEqual(scores["f1"], 0.0)

    def test_partial_unigram_overlap(self):
        scores = rouge_n("rød grøn blå", "rød gul blå", 1)
        self.assertGreater(scores["f1"], 0.0)
        self.assertLess(scores["f1"], 1.0)

    def test_empty_both_sides(self):
        self.assertEqual(rouge_n("", "", 1)["f1"], 1.0)

    def test_empty_prediction(self):
        self.assertEqual(rouge_n("", "tekst her", 1)["f1"], 0.0)


class RougeCliTests(unittest.TestCase):
    def test_cli_exits_zero(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main([])
        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("ROUGE-1", output)
        self.assertIn("identity check", output)
        self.assertIn("1.000", output)


if __name__ == "__main__":
    unittest.main()
