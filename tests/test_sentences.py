import unittest

from silverlab.sentences import split_sentences


class SentenceTests(unittest.TestCase):
    def test_plain_pair(self) -> None:
        text = "Observatoriet åbner lørdag. Børn kommer gratis."
        self.assertEqual(
            split_sentences(text),
            ["Observatoriet åbner lørdag.", "Børn kommer gratis."],
        )

    def test_abbreviation_dr_and_kl(self) -> None:
        text = "Dr. Hansen kommer kl. 19. Han tager toget."
        sentences = split_sentences(text)
        self.assertEqual(len(sentences), 2)
        self.assertTrue(sentences[0].startswith("Dr. Hansen"))
        self.assertTrue(sentences[1].startswith("Han tager"))

    def test_feks_stays_inside_sentence(self) -> None:
        text = "F.eks. kan man se Saturn. Børn kommer gratis."
        sentences = split_sentences(text)
        self.assertEqual(len(sentences), 2)
        self.assertIn("Saturn", sentences[0])

    def test_kr_can_end_a_sentence(self) -> None:
        text = "Billetten koster 25 kr. Hallen åbner lørdag."
        self.assertEqual(
            split_sentences(text),
            ["Billetten koster 25 kr.", "Hallen åbner lørdag."],
        )

    def test_decimal_does_not_split(self) -> None:
        text = "Prisen er 12.5 kroner. Billetten gælder i dag."
        sentences = split_sentences(text)
        self.assertEqual(len(sentences), 2)
        self.assertIn("12.5", sentences[0])

    def test_bla_and_ca(self) -> None:
        text = "Der kommer bl.a. en kvartet og ca. 80 gæster. Døren åbner kl. 19."
        sentences = split_sentences(text)
        self.assertEqual(len(sentences), 2)

    def test_blank(self) -> None:
        self.assertEqual(split_sentences(""), [])
        self.assertEqual(split_sentences("   "), [])

    def test_lab_01_has_several_sentences(self) -> None:
        from silverlab.fiction import brief_by_id

        sentences = split_sentences(brief_by_id("lab-01").article_text)
        self.assertGreaterEqual(len(sentences), 5)
        self.assertTrue(sentences[0].startswith("Himmerlands Observatorium"))
