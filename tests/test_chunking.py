import unittest

from danish_news_summarization.chunking import (
    WhitespaceTokenizer,
    pack_sentences_by_length,
    split_article,
    split_into_sentences,
    split_long_sentence,
)
from danish_news_summarization.sample_data import SAMPLE_ARTICLES, get_article


class SplitLongSentenceTests(unittest.TestCase):
    def test_short_sentence_stays_one_chunk(self) -> None:
        self.assertEqual(split_long_sentence("Kort sætning.", 80), ["Kort sætning."])

    def test_splits_at_comma_before_budget(self) -> None:
        sentence = "Alpha beta gamma, delta epsilon zeta, eta theta iota"
        chunks = split_long_sentence(sentence, max_length=24)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(any("," in chunk for chunk in chunks[:-1]))

    def test_empty_sentence(self) -> None:
        self.assertEqual(split_long_sentence("", 10), [])

    def test_length_fn_refines_oversized_chunk(self) -> None:
        sentence = "one two three four five six seven eight nine ten"
        chunks = split_long_sentence(sentence, max_length=4, length_fn=lambda text: len(text.split()))
        self.assertTrue(all(len(chunk.split()) <= 4 for chunk in chunks))
        self.assertEqual(" ".join(chunks).split(), sentence.split())


class PackSentencesTests(unittest.TestCase):
    def test_packs_until_budget(self) -> None:
        pairs = [("a", 3), ("b", 3), ("c", 5)]
        packed = pack_sentences_by_length(pairs, max_length=6)
        self.assertEqual(packed, [["a", "b"], ["c"]])

    def test_single_overlong_item_gets_its_own_window(self) -> None:
        packed = pack_sentences_by_length([("huge", 20)], max_length=6)
        self.assertEqual(packed, [["huge"]])


class SplitArticleTests(unittest.TestCase):
    def test_sample_article_produces_multiple_windows(self) -> None:
        article = get_article("dn-009")
        tokenizer = WhitespaceTokenizer()
        chunks = split_article(article.body, text_max_length=40, tokenizer=tokenizer)
        self.assertGreaterEqual(len(chunks), 3)
        for chunk in chunks:
            # WhitespaceTokenizer.encode adds 2 special tokens.
            self.assertLessEqual(len(tokenizer.encode(chunk)), 40 + 8)

    def test_every_sample_survives_round_trip_words(self) -> None:
        tokenizer = WhitespaceTokenizer()
        for article in SAMPLE_ARTICLES:
            chunks = split_article(article.body, 50, tokenizer)
            joined = " ".join(chunks)
            self.assertGreater(len(joined), 40)
            self.assertIn(article.body.split()[0], joined)

    def test_split_into_sentences_returns_lists(self) -> None:
        windows = split_into_sentences("En sætning. To sætning. Tre sætning.", 8, WhitespaceTokenizer())
        self.assertTrue(all(isinstance(window, list) for window in windows))
        self.assertGreaterEqual(len(windows), 1)


if __name__ == "__main__":
    unittest.main()
