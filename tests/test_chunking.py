from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.dns_examples.chunking import (
    CharacterBudget,
    WhitespaceCounter,
    pack_sentences,
    split_into_sentence_groups,
    split_long_sentence,
    tidy_joined_tokens,
)
from examples.dns_examples.sentences import word_tokenize


class SplitLongSentenceTests(unittest.TestCase):
    def test_soft_break_on_comma(self) -> None:
        sentence = "Alpha, beta, gamma."
        # character walker: each ", " break happens while under a generous budget
        chunks = split_long_sentence(sentence, max_length=40)
        self.assertGreaterEqual(len(chunks), 1)
        joined = tidy_joined_tokens(" ".join(chunks))
        # All content words survive.
        for word in ("Alpha", "beta", "gamma"):
            self.assertIn(word, joined)

    def test_hard_break_when_no_comma(self) -> None:
        sentence = "one two three four five six seven"
        chunks = split_long_sentence(sentence, max_length=12)
        self.assertGreater(len(chunks), 1)
        reconstructed = [token for chunk in chunks for token in word_tokenize(chunk) if token.isalpha()]
        self.assertEqual(reconstructed, sentence.split())

    def test_short_sentence_stays_one_chunk(self) -> None:
        self.assertEqual(split_long_sentence("Hej.", max_length=80), ["Hej ."])


class PackSentencesTests(unittest.TestCase):
    def test_packs_until_overflow(self) -> None:
        counter = CharacterBudget()
        groups = pack_sentences(["aa", "bb", "cccc"], max_length=5, counter=counter)
        # "aa"(2)+"bb"(2)=4, "cccc"(4) starts a new group
        self.assertEqual(groups, [["aa", "bb"], ["cccc"]])

    def test_single_oversized_piece_is_its_own_group(self) -> None:
        counter = CharacterBudget()
        groups = pack_sentences(["toolong"], max_length=3, counter=counter)
        self.assertEqual(groups, [["toolong"]])

    def test_empty_input(self) -> None:
        self.assertEqual(pack_sentences([], max_length=10, counter=CharacterBudget()), [])


class SplitIntoGroupsTests(unittest.TestCase):
    def test_two_short_sentences_one_group(self) -> None:
        article = "Hej med dig. Farvel så."
        groups = split_into_sentence_groups(article, max_length=80, counter=WhitespaceCounter())
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 2)

    def test_small_budget_splits_groups(self) -> None:
        article = "Hej med dig. Farvel så igen."
        groups = split_into_sentence_groups(article, max_length=6, counter=WhitespaceCounter())
        self.assertGreaterEqual(len(groups), 2)

    def test_translate_back_mode_skips_comma_breaker(self) -> None:
        # One long comma-heavy sentence: without the breaker it stays one piece.
        article = (
            "Fiskerne mødtes, pegede på kutterne, isværket, auktionen, "
            "familierne, og krævede en høring inden jul."
        )
        groups = split_into_sentence_groups(
            article,
            max_length=8,
            counter=WhitespaceCounter(),
            split_oversized=False,
        )
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 1)


class TidyJoinTests(unittest.TestCase):
    def test_strips_space_before_period(self) -> None:
        self.assertEqual(tidy_joined_tokens("Havnen ."), "Havnen.")


if __name__ == "__main__":
    unittest.main()
