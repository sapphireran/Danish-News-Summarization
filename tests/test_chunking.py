import unittest

from danish_summarization.chunking import (
    chunk_article,
    split_into_sentence_batches,
    split_long_sentence,
    text_max_length,
)


class TextMaxLengthTests(unittest.TestCase):
    def test_default_budget_is_ninety_percent_of_512(self):
        self.assertEqual(text_max_length(), 460)

    def test_rejects_non_positive_max_length(self):
        with self.assertRaises(ValueError):
            text_max_length(0)

    def test_rejects_ratio_outside_unit_interval(self):
        with self.assertRaises(ValueError):
            text_max_length(512, 0)
        with self.assertRaises(ValueError):
            text_max_length(512, 1.5)


class SplitLongSentenceTests(unittest.TestCase):
    def test_empty_sentence_returns_no_chunks(self):
        self.assertEqual(split_long_sentence("   ", 20), [])

    def test_short_sentence_stays_in_one_chunk(self):
        sentence = "Byrådet vedtog forslaget i går."
        self.assertEqual(split_long_sentence(sentence, 200), [sentence])

    def test_splits_on_comma_before_the_limit(self):
        sentence = "Første del, anden del, tredje del"
        chunks = split_long_sentence(sentence, 20)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(any(chunk.endswith(",") for chunk in chunks[:-1]))

    def test_hard_splits_when_there_is_no_comma(self):
        words = " ".join(f"ord{i}" for i in range(12))
        chunks = split_long_sentence(words, 18)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(" ".join(chunks), words)


class SentenceBatchTests(unittest.TestCase):
    def test_empty_article_returns_no_batches(self):
        self.assertEqual(split_into_sentence_batches(""), [])

    def test_packs_short_sentences_together(self):
        article = "Første sætning. Anden sætning. Tredje sætning."
        batches = split_into_sentence_batches(article, max_length=40, ratio=1.0)
        self.assertEqual(len(batches), 1)
        self.assertEqual(len(batches[0]), 3)

    def test_starts_a_new_batch_when_budget_is_exceeded(self):
        article = (
            "Den første sætning er allerede ret lang og fylder godt. "
            "Den anden sætning er også lang og skal i næste batch."
        )
        batches = split_into_sentence_batches(
            article,
            max_length=12,
            ratio=1.0,
            length_fn=lambda text: len(text.split()),
        )
        self.assertEqual(len(batches), 2)
        self.assertEqual(len(batches[0]), 1)
        self.assertEqual(len(batches[1]), 1)

    def test_chunk_article_joins_each_batch(self):
        article = "Alpha. Bravo. Charlie."
        chunks = chunk_article(article, max_length=80, ratio=1.0)
        self.assertEqual(chunks, ["Alpha. Bravo. Charlie."])

    def test_respects_pre_split_sentences(self):
        batches = split_into_sentence_batches(
            "ignored",
            max_length=20,
            ratio=1.0,
            sentences=["Kort.", "Også kort."],
        )
        self.assertEqual(batches, [["Kort.", "Også kort."]])


if __name__ == "__main__":
    unittest.main()
