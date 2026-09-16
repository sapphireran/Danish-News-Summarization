import unittest

from danish_news_summarization.text import join_words, sent_tokenize, word_tokenize


class SentenceTokenizerTests(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertEqual(sent_tokenize(""), [])
        self.assertEqual(sent_tokenize("   "), [])

    def test_splits_on_period(self) -> None:
        text = "Byrådet sagde ja. Naboerne er stadig uenige."
        self.assertEqual(
            sent_tokenize(text),
            ["Byrådet sagde ja.", "Naboerne er stadig uenige."],
        )

    def test_keeps_decimal_commas_and_abbreviations(self) -> None:
        text = (
            "Rammen er 2,4 millioner kroner, t.eks. til busser. "
            "Bibliotekerne åbner til kl. 21 på hverdage."
        )
        sentences = sent_tokenize(text)
        self.assertEqual(len(sentences), 2)
        self.assertIn("2,4 millioner", sentences[0])
        self.assertTrue(sentences[1].startswith("Bibliotekerne"))

    def test_question_and_exclaim(self) -> None:
        text = "Virker det på gamle telefoner? Elevrådet er i tvivl! Forvaltningen svarer i morgen."
        self.assertEqual(len(sent_tokenize(text)), 3)

    def test_keeps_skt_hans_together(self) -> None:
        text = "Uheld ved Elmegade og Skt. Hans Torv steg. Politiet efterforsker sagen."
        sentences = sent_tokenize(text)
        self.assertEqual(len(sentences), 2)
        self.assertIn("Skt. Hans Torv", sentences[0])


class WordTokenizerTests(unittest.TestCase):
    def test_keeps_punctuation_as_tokens(self) -> None:
        tokens = word_tokenize("Hej, Aarhus!")
        self.assertEqual(tokens, ["Hej", ",", "Aarhus", "!"])

    def test_join_glues_punctuation(self) -> None:
        self.assertEqual(join_words(["Hej", ",", "Aarhus", "!"]), "Hej, Aarhus!")


if __name__ == "__main__":
    unittest.main()
