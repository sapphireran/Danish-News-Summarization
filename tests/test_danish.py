import unittest

from kystlinje.danish import lead_n, normalize, split_sentences, word_tokenize


class SentenceSplitTests(unittest.TestCase):
    def test_simple_period(self) -> None:
        text = "Huset er rødt. Haven er grøn."
        self.assertEqual(split_sentences(text), ["Huset er rødt.", "Haven er grøn."])

    def test_abbreviation_kr_does_not_split_before_lowercase(self) -> None:
        text = "Billetten koster 40 kr. for voksne og 10 kr. for børn."
        self.assertEqual(len(split_sentences(text)), 1)

    def test_abbreviation_kr_does_split_before_capital(self) -> None:
        text = "Prisen er 15 kr. Pressen kræver to personer."
        sents = split_sentences(text)
        self.assertEqual(len(sents), 2)
        self.assertTrue(sents[1].startswith("Pressen"))

    def test_decimal_comma_stays_together(self) -> None:
        text = "Dr. Holm målte 3,5 km. siden morgen."
        sents = split_sentences(text)
        self.assertEqual(len(sents), 1)
        self.assertIn("3,5", sents[0])

    def test_kl_before_time(self) -> None:
        text = "Færgen går kl. 23:40 fra Hjelmhøj."
        self.assertEqual(len(split_sentences(text)), 1)

    def test_lead_n(self) -> None:
        text = "En. To. Tre."
        self.assertEqual(lead_n(text, 2), "En. To.")


class TokenizeTests(unittest.TestCase):
    def test_time_is_one_token(self) -> None:
        self.assertIn("23:40", word_tokenize("kl. 23:40 fra kajen"))

    def test_punctuation_is_split(self) -> None:
        tokens = word_tokenize("Hej, Signe!")
        self.assertIn(",", tokens)
        self.assertIn("Signe", tokens)

    def test_normalize_casefold(self) -> None:
        self.assertEqual(normalize("Æblehaven"), "æblehaven")


if __name__ == "__main__":
    unittest.main()
