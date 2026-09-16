import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.danish_sentences import split_danish_sentences, word_tokenize


class SentenceSplitTests(unittest.TestCase):
    def test_empty_and_whitespace(self):
        self.assertEqual(split_danish_sentences(""), [])
        self.assertEqual(split_danish_sentences("   \n"), [])
        self.assertEqual(split_danish_sentences(None), [])

    def test_two_news_sentences(self):
        text = "Haven åbnede lørdag. Over 200 gæster kom forbi."
        self.assertEqual(
            split_danish_sentences(text),
            ["Haven åbnede lørdag.", "Over 200 gæster kom forbi."],
        )

    def test_abbreviation_does_not_split(self):
        text = "Vindstødene ramte ca. 28 meter i sekundet, og turen kl. 21.15 blev aflyst."
        sentences = split_danish_sentences(text)
        self.assertEqual(len(sentences), 1)
        self.assertIn("ca. 28", sentences[0])
        self.assertIn("kl. 21.15", sentences[0])

    def test_initials_and_ordinal_date(self):
        text = "Mødet er den 3. april hos A. Vestergaard i pakhuset."
        sentences = split_danish_sentences(text)
        self.assertEqual(len(sentences), 1)
        self.assertIn("3. april", sentences[0])
        self.assertIn("A. Vestergaard", sentences[0])

    def test_question_and_exclaim(self):
        text = "Kommer færgen? Ja! Terminalen er åben."
        self.assertEqual(
            split_danish_sentences(text),
            ["Kommer færgen?", "Ja!", "Terminalen er åben."],
        )

    def test_trailing_fragment_without_period(self):
        text = "Første sætning. Anden sætning uden punktum"
        self.assertEqual(
            split_danish_sentences(text),
            ["Første sætning.", "Anden sætning uden punktum"],
        )

    def test_thousands_separator_stays_inside_sentence(self):
        text = "Kommunen har støttet anlægget med 340.000 kroner."
        self.assertEqual(len(split_danish_sentences(text)), 1)


class WordTokenizeTests(unittest.TestCase):
    def test_words_and_punctuation(self):
        tokens = word_tokenize("3-1 over Havnkær.")
        self.assertIn("3-1", tokens)
        self.assertIn("Havnkær", tokens)
        self.assertIn(".", tokens)

    def test_empty(self):
        self.assertEqual(word_tokenize(""), [])


if __name__ == "__main__":
    unittest.main()
