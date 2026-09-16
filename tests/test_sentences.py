import unittest

from maalestok.sentences import split_sentences


class SentenceTests(unittest.TestCase):
    def test_keeps_time_and_currency_abbreviations(self) -> None:
        text = "Billetten koster 18 kr. Bussen går kl. 8.15 fra Nørreled."
        parts = split_sentences(text)
        self.assertEqual(len(parts), 2)
        self.assertIn("18 kr.", parts[0])
        self.assertIn("kl. 8.15", parts[1])

    def test_keeps_tex_and_st_hans(self) -> None:
        text = "Skolen minder om Skt. Hans, t.eks. når 1. klasse går til åen. Det tæller."
        parts = split_sentences(text)
        self.assertEqual(len(parts), 2)
        self.assertIn("t.eks.", parts[0])
        self.assertIn("1. klasse", parts[0])

    def test_keeps_ordinal_date(self) -> None:
        text = "Regnen faldt den 12. juni. Aftensangen blev aflyst."
        parts = split_sentences(text)
        self.assertEqual(parts[0], "Regnen faldt den 12. juni.")
        self.assertEqual(parts[1], "Aftensangen blev aflyst.")

    def test_splits_after_year(self) -> None:
        text = "Rekorden er fra 2015. Den står stadig."
        parts = split_sentences(text)
        self.assertEqual(len(parts), 2)
        self.assertTrue(parts[0].endswith("2015."))

    def test_weekday_range_stays_one_sentence(self) -> None:
        text = "Biblioteket har åbent man.–tors. 13.00–17.00 i vinter."
        parts = split_sentences(text)
        self.assertEqual(len(parts), 1)


if __name__ == "__main__":
    unittest.main()
