"""Chunker behavior, including the mixed char/token budget from 2023."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXAMPLES_DIR))

from corpus import by_id  # noqa: E402
from text_chunking import (  # noqa: E402
    default_encode_length,
    pack_sentences,
    report_chunks,
    split_article,
    split_long_sentence,
    split_sentences,
    word_tokenize,
)


class SentenceSplitTests(unittest.TestCase):
    def test_splits_on_period(self) -> None:
        text = "Første sætning. Anden sætning! Tredje spørgsmål?"
        self.assertEqual(len(split_sentences(text)), 3)

    def test_keeps_abbreviation(self) -> None:
        text = "Kommunen åbner f.eks. et nyt hus. Det sker mandag."
        pieces = split_sentences(text)
        self.assertEqual(len(pieces), 2)
        self.assertIn("f.eks.", pieces[0])

    def test_empty(self) -> None:
        self.assertEqual(split_sentences("   "), [])


class WordTokenizeTests(unittest.TestCase):
    def test_splits_comma(self) -> None:
        tokens = word_tokenize("kaj, promenade og landstrøm")
        self.assertIn(",", tokens)
        self.assertIn("promenade", tokens)


class LongSentenceTests(unittest.TestCase):
    def test_char_budget_cuts_before_overflow(self) -> None:
        sentence = "alpha, beta, gamma, delta, epsilon"
        chunks = split_long_sentence(sentence, max_length=14, length_unit="chars")
        self.assertGreaterEqual(len(chunks), 2)
        for chunk in chunks:
            # Original rule: running len(word)+1 compared to max_length.
            self.assertLessEqual(sum(len(tok) + 1 for tok in word_tokenize(chunk)), 20)

    def test_soft_break_on_comma(self) -> None:
        sentence = "one, two, three"
        chunks = split_long_sentence(sentence, max_length=10, length_unit="chars")
        self.assertGreaterEqual(len(chunks), 2)

    def test_empty_sentence(self) -> None:
        self.assertEqual(split_long_sentence("", 10), [])


class PackTests(unittest.TestCase):
    def test_packs_under_budget(self) -> None:
        pairs = [("a", 3), ("b", 3), ("c", 5)]
        batches = pack_sentences(pairs, text_max_length=7)
        self.assertEqual(batches, [["a", "b"], ["c"]])

    def test_single_oversize_stays_alone(self) -> None:
        batches = pack_sentences([("long", 12)], text_max_length=7)
        self.assertEqual(batches, [["long"]])


class EncodeLengthTests(unittest.TestCase):
    def test_counts_words_plus_two(self) -> None:
        self.assertEqual(default_encode_length("tre korte ord"), 5)


class ArticleChunkTests(unittest.TestCase):
    def test_harbor_article_splits_on_demo_budget(self) -> None:
        article = by_id()["dn-006"]
        chunks = split_article(article.body_da, text_max_length=28)
        self.assertGreaterEqual(len(chunks), 2)
        for chunk in chunks:
            self.assertLessEqual(default_encode_length(chunk), 28)
        joined = " ".join(chunks)
        self.assertIn("Frederikshavn", joined)
        self.assertIn("187", joined)

    def test_short_article_is_single_chunk_on_large_budget(self) -> None:
        article = by_id()["dn-001"]
        chunks = split_article(article.body_da, text_max_length=400)
        self.assertEqual(len(chunks), 1)

    def test_report_fields(self) -> None:
        article = by_id()["dn-003"]
        report = report_chunks(article.id, article.body_da, 40)
        self.assertEqual(report.article_id, "dn-003")
        self.assertEqual(report.n_chunks, len(report.chunks))
        self.assertEqual(report.n_chunks, len(report.chunk_lengths))


if __name__ == "__main__":
    unittest.main()
