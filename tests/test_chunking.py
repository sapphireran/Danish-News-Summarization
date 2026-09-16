from __future__ import annotations

import sys
import unittest
from pathlib import Path

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))

from chunking import (
    char_budget_len,
    default_text_max_length,
    simple_sent_tokenize,
    simple_word_tokenize,
    split_article,
    split_into_windows,
    split_long_sentence,
    window_stats,
    windows_to_text,
)


class TokenizeTests(unittest.TestCase):
    def test_word_tokenize_peels_comma(self) -> None:
        self.assertEqual(
            simple_word_tokenize("hej, verden"),
            ["hej", ",", "verden"],
        )

    def test_sent_tokenize_splits_on_period(self) -> None:
        text = "Første sætning. Anden sætning! Tredje?"
        self.assertEqual(
            simple_sent_tokenize(text),
            ["Første sætning.", "Anden sætning!", "Tredje?"],
        )

    def test_empty_and_whitespace(self) -> None:
        self.assertEqual(simple_sent_tokenize(""), [])
        self.assertEqual(simple_sent_tokenize("   "), [])
        self.assertEqual(simple_word_tokenize(""), [])


class SplitLongSentenceTests(unittest.TestCase):
    def test_short_sentence_stays_one_chunk(self) -> None:
        sentence = "Det er en kort sætning."
        chunks = split_long_sentence(sentence, max_length=400)
        self.assertEqual(len(chunks), 1)
        self.assertIn("kort", chunks[0])

    def test_comma_flushes_while_under_budget(self) -> None:
        sentence = "alfa, beta, gamma"
        chunks = split_long_sentence(sentence, max_length=400)
        # Course quirk: every comma under budget starts a new chunk.
        self.assertEqual(len(chunks), 3)
        self.assertTrue(chunks[0].endswith(","))
        self.assertTrue(chunks[1].endswith(","))
        self.assertEqual(chunks[2], "gamma")

    def test_over_budget_without_comma_hard_wraps(self) -> None:
        sentence = "aaaaa bbbbb ccccc"
        chunks = split_long_sentence(sentence, max_length=10)
        self.assertGreaterEqual(len(chunks), 2)
        for chunk in chunks:
            self.assertLessEqual(char_budget_len(chunk), 12)


class PackingTests(unittest.TestCase):
    def test_default_budget_is_ninety_percent_of_512(self) -> None:
        self.assertEqual(default_text_max_length(), 460)

    def test_short_article_is_one_window(self) -> None:
        article = "En sætning. Endnu en sætning."
        windows = split_into_windows(article, text_max_length=400)
        self.assertEqual(len(windows), 1)
        self.assertEqual(len(windows[0]), 2)

    def test_packing_respects_budget(self) -> None:
        article = "Første. Anden. Tredje. Fjerde."
        windows = split_into_windows(article, text_max_length=20)
        self.assertGreaterEqual(len(windows), 2)
        for window in windows:
            self.assertLessEqual(char_budget_len(" ".join(window)), 24)

    def test_drop_empty_skips_blank_window_on_first_overflow(self) -> None:
        huge = "x" * 80
        windows = split_into_windows(huge, text_max_length=10, drop_empty=True)
        self.assertTrue(all(window for window in windows))

    def test_windows_to_text_joins_with_space(self) -> None:
        text = windows_to_text([["En.", "To."], ["Tre."]])
        self.assertEqual(text, ["En. To.", "Tre."])

    def test_split_article_round_trip_contains_words(self) -> None:
        article = "Havnen udvides. Bussene omlægges. Skolen vandt."
        pieces = split_article(article, text_max_length=30)
        joined = " ".join(pieces)
        self.assertIn("Havnen", joined)
        self.assertIn("Skolen", joined)

    def test_window_stats_keys(self) -> None:
        stats = window_stats("En sætning. To sætninger.", text_max_length=400)
        self.assertEqual(stats["sentences"], 2)
        self.assertEqual(stats["windows"], 1)
        self.assertGreater(stats["chars"], 0)


if __name__ == "__main__":
    unittest.main()
