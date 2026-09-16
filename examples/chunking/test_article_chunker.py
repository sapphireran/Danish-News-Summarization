#!/usr/bin/env python3
"""Stdlib tests for the documented packer. Run: python examples/chunking/test_article_chunker.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from article_chunker import (
    WhitespaceApproxTokenizer,
    report_pack,
    sent_tokenize,
    split_article,
    split_long_sentence,
    token_len,
)


class SentenceSplitTests(unittest.TestCase):
    def test_two_english_sentences(self) -> None:
        parts = sent_tokenize("The ferry is cancelled. The hall stays open.")
        self.assertGreaterEqual(len(parts), 2)
        self.assertTrue(parts[0].startswith("The ferry"))

    def test_empty(self) -> None:
        self.assertEqual(sent_tokenize("   "), [])


class LongSentenceTests(unittest.TestCase):
    def test_splits_on_comma_under_budget(self) -> None:
        text = "alpha, beta, gamma, delta"
        pieces = split_long_sentence(text, max_length=12)
        self.assertGreaterEqual(len(pieces), 2)
        for piece in pieces:
            # character heuristic: each flush is under or around the budget
            self.assertLessEqual(len(piece), 20)

    def test_single_short_sentence_stays_one_chunk(self) -> None:
        pieces = split_long_sentence("Short.", max_length=80)
        self.assertEqual(len(pieces), 1)


class PackTests(unittest.TestCase):
    def test_short_article_is_one_chunk(self) -> None:
        tok = WhitespaceApproxTokenizer()
        chunks = split_article("One short sentence stays together.", 64, tok)
        self.assertEqual(len(chunks), 1)

    def test_long_article_uses_several_chunks(self) -> None:
        tok = WhitespaceApproxTokenizer()
        text = " ".join(f"Sentence number {i} is padding for the packer." for i in range(40))
        chunks = split_article(text, 40, tok)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(token_len(chunk, tok), 40)

    def test_report_fields(self) -> None:
        report = report_pack("Hello there. More words follow now.", 8)
        self.assertGreater(report.article_chars, 0)
        self.assertEqual(report.n_chunks, len(report.chunks))
        self.assertEqual(len(report.chunk_token_lengths), report.n_chunks)


if __name__ == "__main__":
    unittest.main()
