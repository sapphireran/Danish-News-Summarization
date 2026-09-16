from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.dns_examples.sentences import split_sentences, word_tokenize


class WordTokenizeTests(unittest.TestCase):
    def test_splits_punctuation(self) -> None:
        tokens = word_tokenize("Havnen, ja.")
        self.assertEqual(tokens, ["Havnen", ",", "ja", "."])

    def test_keeps_danish_letters(self) -> None:
        tokens = word_tokenize("Æbleøen åbner")
        self.assertEqual(tokens, ["Æbleøen", "åbner"])

    def test_empty(self) -> None:
        self.assertEqual(word_tokenize(""), [])


class SplitSentencesTests(unittest.TestCase):
    def test_period_space_capital(self) -> None:
        text = "Første sætning. Anden sætning! Tredje?"
        self.assertEqual(split_sentences(text), ["Første sætning.", "Anden sætning!", "Tredje?"])

    def test_danish_decimal_comma_is_not_a_boundary(self) -> None:
        text = "Stien koster 4,2 millioner kroner. Gravearbejdet begynder i uge 12."
        self.assertEqual(len(split_sentences(text)), 2)

    def test_abbreviation_ca(self) -> None:
        text = "Mødet varer ca. to timer. Derefter kaffe."
        self.assertEqual(split_sentences(text), ["Mødet varer ca. to timer.", "Derefter kaffe."])

    def test_title_abbreviation(self) -> None:
        text = "Dr. Hansen kommer i morgen. Kaffen står klar."
        self.assertEqual(split_sentences(text), ["Dr. Hansen kommer i morgen.", "Kaffen står klar."])

    def test_single_long_sentence(self) -> None:
        text = (
            "Fiskerne mødtes for at protestere, pegede på kuttere, isværket, "
            "auktionen, og krævede en høring inden jul."
        )
        self.assertEqual(len(split_sentences(text)), 1)

    def test_blank(self) -> None:
        self.assertEqual(split_sentences("   "), [])
        self.assertEqual(split_sentences(""), [])


if __name__ == "__main__":
    unittest.main()
