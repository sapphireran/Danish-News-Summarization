import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.text_chunking import (
    pack_units,
    split_into_sentence_batches,
    split_long_sentence,
    word_length,
)


class PackUnitsTests(unittest.TestCase):
    def test_packs_until_budget(self):
        units = [("a", 2), ("b", 2), ("c", 3)]
        self.assertEqual(pack_units(units, max_length=4), [["a", "b"], ["c"]])

    def test_single_unit_over_budget_starts_its_own_batch(self):
        units = [("short", 2), ("very-long", 10)]
        self.assertEqual(pack_units(units, max_length=4), [["short"], ["very-long"]])

    def test_rejects_bad_budget(self):
        with self.assertRaises(ValueError):
            pack_units([("a", 1)], max_length=0)

    def test_empty(self):
        self.assertEqual(pack_units([], max_length=8), [])


class SplitLongSentenceTests(unittest.TestCase):
    def test_near_limit_keeps_short_sentence(self):
        text = "Det er en kort sætning, med et komma."
        chunks = split_long_sentence(text, max_length=200, mode="near_limit")
        self.assertEqual(chunks, [text])

    def test_historical_mode_flushes_at_each_comma(self):
        text = "Et, to, tre."
        chunks = split_long_sentence(text, max_length=200, mode="historical")
        # Historical 2023 behaviour: every comma under the limit starts a new chunk.
        self.assertGreater(len(chunks), 1)
        self.assertTrue(chunks[0].endswith(","))

    def test_near_limit_splits_oversized_clause(self):
        words = ["ord"] * 30
        text = " ".join(words)
        chunks = split_long_sentence(text, max_length=10, mode="near_limit", length_fn=word_length)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(word_length(chunk), 10)

    def test_rejects_unknown_mode(self):
        with self.assertRaises(ValueError):
            split_long_sentence("hej", max_length=8, mode="nope")


class ArticleBatchTests(unittest.TestCase):
    def test_sample_harbor_article_needs_several_batches(self):
        from examples.sample_catalog import by_id

        article = by_id()["ex-006-havn"]["body_da"]
        batches = split_into_sentence_batches(article, max_length=40, mode="near_limit")
        self.assertGreaterEqual(len(batches), 3)
        rebuilt = " ".join(unit for batch in batches for unit in batch)
        # All source sentences should still be present after packing.
        self.assertIn("62 millioner", rebuilt)
        self.assertIn("pakhus 2", rebuilt)

    def test_tiny_article_is_one_batch(self):
        batches = split_into_sentence_batches("Haven åbnede lørdag.", max_length=40)
        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0], ["Haven åbnede lørdag."])


if __name__ == "__main__":
    unittest.main()
