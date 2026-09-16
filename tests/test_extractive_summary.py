import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.extractive_summary import content_tokens, extractive_summarize, sentence_scores
from examples.sample_catalog import SAMPLES


class ExtractiveSummaryTests(unittest.TestCase):
    def test_empty_text(self):
        self.assertEqual(extractive_summarize(""), "")

    def test_single_sentence_passthrough(self):
        text = "Biblioteket åbnede en læsehave."
        self.assertEqual(extractive_summarize(text, max_sentences=2), text)

    def test_prefers_content_heavy_sentence(self):
        text = (
            "Det er det. "
            "Læsehaven i Østerhavn åbnede med bænke, pilehegn og højtlæsning. "
            "Og så videre."
        )
        summary = extractive_summarize(text, max_sentences=1, max_chars=None)
        self.assertIn("Læsehaven", summary)
        self.assertNotIn("Og så videre", summary)

    def test_respects_char_budget(self):
        text = SAMPLES[-1]["body_da"]
        summary = extractive_summarize(text, max_sentences=3, max_chars=160)
        self.assertLessEqual(len(summary), 160)
        self.assertTrue(summary)

    def test_rejects_non_positive_k(self):
        with self.assertRaises(ValueError):
            extractive_summarize("Hej.", max_sentences=0)

    def test_content_tokens_drop_stopwords(self):
        tokens = content_tokens("Det er en havn i Klitvig og det er stort.")
        self.assertIn("havn", tokens)
        self.assertIn("klitvig", tokens)
        self.assertNotIn("det", tokens)
        self.assertNotIn("er", tokens)

    def test_scores_align_with_sentence_count(self):
        sentences = ["Kort.", "Klitvig Havn renoverer kajen efter stormfloden."]
        scores = sentence_scores(sentences)
        self.assertEqual(len(scores), 2)
        self.assertGreater(scores[1], scores[0])


if __name__ == "__main__":
    unittest.main()
