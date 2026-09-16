import unittest

from examples.text_chunking import (
    default_length,
    pack_article,
    pack_sentences,
    split_long_sentence,
    split_sentences,
)


class SplitSentencesTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(split_sentences("   "), [])

    def test_single_sentence(self):
        self.assertEqual(split_sentences("Hjørring holder møde."), ["Hjørring holder møde."])

    def test_multiple_sentences(self):
        text = "Første sætning. Anden sætning! Tredje sætning?"
        self.assertEqual(
            split_sentences(text),
            ["Første sætning.", "Anden sætning!", "Tredje sætning?"],
        )

    def test_collapses_whitespace(self):
        text = "Linje et.\n\n   Linje to."
        self.assertEqual(split_sentences(text), ["Linje et.", "Linje to."])


class SplitLongSentenceTests(unittest.TestCase):
    def test_short_sentence_stays_one_chunk(self):
        self.assertEqual(split_long_sentence("kort tekst", max_length=80), ["kort tekst"])

    def test_flushes_on_comma_before_budget(self):
        sentence = "alpha, beta, gamma"
        chunks = split_long_sentence(sentence, max_length=20)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(any(chunk.endswith(",") for chunk in chunks[:-1]))

    def test_overflow_without_comma_splits_words(self):
        sentence = "aaaaa bbbbb ccccc ddddd eeeee"
        chunks = split_long_sentence(sentence, max_length=12)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(" ".join(chunks).replace("  ", " "), sentence)

    def test_length_fn_repairs_overlong_chunk(self):
        def char_len(text: str) -> int:
            return len(text)

        sentence = "one two three four five six seven eight"
        chunks = split_long_sentence(sentence, max_length=12, length_fn=char_len)
        self.assertTrue(all(char_len(chunk) <= 12 or " " not in chunk for chunk in chunks))
        self.assertEqual(" ".join(chunks).split(), sentence.split())


class PackTests(unittest.TestCase):
    def test_pack_sentences_starts_new_list_when_over_budget(self):
        packed = pack_sentences(
            [("a", 3), ("b", 3), ("c", 3)],
            text_max_length=5,
        )
        self.assertEqual(packed, [["a"], ["b"], ["c"]])

    def test_pack_sentences_keeps_items_that_fit(self):
        packed = pack_sentences(
            [("a", 2), ("b", 2), ("c", 2)],
            text_max_length=5,
        )
        self.assertEqual(packed, [["a", "b"], ["c"]])

    def test_pack_article_single_chunk_for_short_text(self):
        article = "Aalborg bibliotek ændrer åbningstider. Søndag forbliver lukket."
        chunks = pack_article(article, text_max_length=200)
        self.assertEqual(len(chunks), 1)
        self.assertIn("Aalborg", chunks[0])

    def test_pack_article_multiple_chunks_with_tiny_budget(self):
        article = "Første sætning her. Anden sætning der. Tredje sætning igen."
        chunks = pack_article(article, text_max_length=4)
        self.assertGreaterEqual(len(chunks), 2)

    def test_default_length_counts_words_plus_one(self):
        self.assertEqual(default_length(""), 1)
        self.assertEqual(default_length("to words"), 3)


class SampleArticlePackTests(unittest.TestCase):
    def test_library_article_fits_marian_budget(self):
        from examples.schemas import read_csv
        from pathlib import Path

        rows = read_csv(Path("examples/sample_data/00_raw_articles.csv"))
        body = next(row["article text"] for row in rows if row["id"] == "aalborg-library-hours")
        chunks = pack_article(body, text_max_length=460)
        self.assertEqual(len(chunks), 1)
        self.assertLessEqual(default_length(chunks[0]), 460)


if __name__ == "__main__":
    unittest.main()
