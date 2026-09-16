import unittest

from silverlab.tokenize import content_tokens, ngrams, tokenize


class TokenizeTests(unittest.TestCase):
    def test_keeps_danish_vowels(self) -> None:
        tokens = tokenize("Æblekagen smager sødt på åen.")
        self.assertIn("æblekagen", tokens)
        self.assertIn("sødt", tokens)
        self.assertIn("åen", tokens)

    def test_folds_case(self) -> None:
        self.assertEqual(tokenize("Saturn"), tokenize("saturn"))

    def test_empty(self) -> None:
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize(None), [])  # type: ignore[arg-type]

    def test_content_tokens_drop_stopwords_and_digits(self) -> None:
        tokens = content_tokens("Og de 80 gæster ser Saturn")
        self.assertNotIn("og", tokens)
        self.assertNotIn("de", tokens)
        self.assertNotIn("80", tokens)
        self.assertIn("gæster", tokens)
        self.assertIn("saturn", tokens)

    def test_ngrams(self) -> None:
        self.assertEqual(ngrams(["a", "b", "c"], 2), [("a", "b"), ("b", "c")])
        self.assertEqual(ngrams(["a"], 2), [])
        self.assertEqual(ngrams(["a", "b"], 0), [])
