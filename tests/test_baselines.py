import unittest

from silverlab.baselines import (
    run_all_baselines,
    summarize_keyword,
    summarize_lead,
    summarize_longest,
    summarize_textrank,
    textrank_scores,
)
from silverlab.fiction import all_briefs, brief_by_id
from silverlab.sentences import split_sentences


class BaselineTests(unittest.TestCase):
    def test_lead1_matches_handwritten_extractive_gold(self) -> None:
        for brief in all_briefs():
            result = summarize_lead(brief.article_text, k=1)
            self.assertEqual(
                result.summary,
                brief.gold_extractive,
                brief.id,
            )

    def test_lead1_is_first_sentence(self) -> None:
        brief = brief_by_id("lab-01")
        first = split_sentences(brief.article_text)[0]
        result = summarize_lead(brief.article_text, k=1)
        self.assertEqual(result.summary, first)
        self.assertEqual(result.sentence_indices, (0,))

    def test_lead2_preserves_order(self) -> None:
        brief = brief_by_id("lab-04")
        sentences = split_sentences(brief.article_text)
        result = summarize_lead(brief.article_text, k=2)
        self.assertEqual(result.summary, f"{sentences[0]} {sentences[1]}")
        self.assertEqual(result.sentence_indices, (0, 1))

    def test_longest_picks_max_token_sentence(self) -> None:
        text = "Kort. Dette er en noget længere sætning om natsværmere. Middel."
        result = summarize_longest(text, k=1)
        self.assertIn("natsværmere", result.summary)
        self.assertEqual(result.sentence_indices, (1,))

    def test_keyword_prefers_title_overlap(self) -> None:
        text = (
            "Der serveres kaffe i teltet. "
            "Saturn vises i teleskopet ved observatoriet. "
            "Børn kommer gratis."
        )
        result = summarize_keyword(text, title="Observatorium viser Saturn", k=1)
        self.assertIn("Saturn", result.summary)

    def test_keyword_falls_back_without_title(self) -> None:
        text = "Første sætning. Anden sætning."
        result = summarize_keyword(text, title="", k=2)
        self.assertEqual(result.name, "keyword")
        self.assertEqual(result.summary, "Første sætning.")

    def test_textrank_single_sentence(self) -> None:
        result = summarize_textrank("Kun en sætning.", k=2)
        self.assertEqual(result.summary, "Kun en sætning.")
        self.assertEqual(textrank_scores(["Kun en sætning."]), [1.0])

    def test_textrank_empty(self) -> None:
        self.assertEqual(summarize_textrank("", k=2).summary, "")
        self.assertEqual(textrank_scores([]), [])

    def test_textrank_returns_original_order(self) -> None:
        text = (
            "Månen står højt over Hobro. "
            "Kaffen er klar i målestationen. "
            "Saturn kan ses i spejlteleskopet ved månen."
        )
        result = summarize_textrank(text, k=2)
        sentences = split_sentences(text)
        joined = result.summary
        # Selected sentences must appear in document order.
        positions = [joined.find(sent) for sent in sentences if sent in joined]
        self.assertEqual(positions, sorted(positions))

    def test_run_all_has_stable_names(self) -> None:
        brief = brief_by_id("lab-16")
        bundle = run_all_baselines(brief.article_text, brief.title)
        self.assertEqual(
            set(bundle),
            {"lead1", "lead2", "longest", "keyword", "textrank"},
        )
        for result in bundle.values():
            self.assertTrue(result.summary)

    def test_empty_article(self) -> None:
        self.assertEqual(summarize_lead("", k=2).summary, "")
        self.assertEqual(summarize_longest("").summary, "")
        self.assertEqual(summarize_keyword("", "titel").summary, "")
