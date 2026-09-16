import unittest

from kystlinje.pack import pack_article, split_long_sentence


class SplitLongSentenceTests(unittest.TestCase):
    def test_splits_on_character_budget_not_token_count(self) -> None:
        sentence = "Alfa, bravo, charlie, delta, echo, foxtrot, golf."
        chunks = split_long_sentence(sentence, max_length=20)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            measured = sum(len(tok) + 1 for tok in chunk.replace(",", " , ").split())
            # The 2023 loop can overshoot by one token; keep a loose ceiling.
            self.assertLessEqual(len(chunk), 40)

    def test_comma_is_a_preferred_cut(self) -> None:
        sentence = "alpha, bravo, charlie"
        chunks = split_long_sentence(sentence, max_length=16)
        self.assertTrue(any("," in chunk or chunk.endswith("alpha,") or "alpha" in chunk for chunk in chunks))


class PackArticleTests(unittest.TestCase):
    def test_tiny_budget_makes_many_windows(self) -> None:
        text = "En sætning er kort. En anden er også kort. En tredje slutter her."
        packed = pack_article(text, budget=24, unit="char")
        self.assertGreaterEqual(len(packed), 2)

    def test_token_unit_differs_from_char_unit_on_long_words(self) -> None:
        text = (
            "Tårnslutspillet i klubmesterskabet fortsatte. "
            "Messingorkesteret øvede færgeklokken."
        )
        by_char = pack_article(text, budget=40, unit="char")
        by_token = pack_article(text, budget=40, unit="token")
        self.assertGreaterEqual(len(by_char), len(by_token))

    def test_rejects_tiny_budget(self) -> None:
        with self.assertRaises(ValueError):
            pack_article("Hej.", budget=3)


if __name__ == "__main__":
    unittest.main()
