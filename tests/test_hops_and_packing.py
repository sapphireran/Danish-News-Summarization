import unittest

from maalestok.corpus import by_id
from maalestok.hops import align_measures, classify_pair
from maalestok.measures import extract_measures
from maalestok.nllb_scar import demo_cases, scar_decode
from maalestok.packing import pack_article, split_long_sentence
from maalestok.tokenize import word_tokenize


class HopTests(unittest.TestCase):
    def test_comma_shift_on_hectares(self) -> None:
        source = extract_measures("Morten høstede 2,4 ha vårbyg.")[0]
        target = extract_measures("Bæk høstede 24 ha vårbyg.")[0]
        pair = classify_pair(source, target)
        self.assertEqual(pair.label, "comma_shift")

    def test_sign_drop(self) -> None:
        source = extract_measures("Det blev −8,3 °C.")[0]
        target = extract_measures("Det blev 8,3 °C.")[0]
        self.assertEqual(classify_pair(source, target).label, "sign_drop")

    def test_clock_12h(self) -> None:
        source = extract_measures("Der ringes ind kl. 8.15.")[0]
        target = extract_measures("Der ringes ind kl. 20.15.")[0]
        self.assertEqual(classify_pair(source, target).label, "clock_12h")

    def test_currency_swap(self) -> None:
        source = extract_measures("Prisen var 3.200 kr.")[0]
        target = extract_measures("Prisen var 3.200 dollar.")[0]
        self.assertEqual(classify_pair(source, target).label, "currency_swap")

    def test_align_bh02_silver(self) -> None:
        article = by_id("bh-02")
        pairs = align_measures(
            extract_measures(article.body_da),
            extract_measures(article.silver_da),
        )
        labels = {p.label for p in pairs}
        self.assertIn("comma_shift", labels)
        self.assertIn("currency_swap", labels)

    def test_same_kind_only_does_not_steal_dates(self) -> None:
        source = extract_measures("Der faldt 18,6 mm den 12. juni kl. 19.00.")
        target = extract_measures("Der faldt 47 mm den 12. juni kl. 19.00.")
        pairs = align_measures(source, target)
        by_src = {p.source.kind: p.label for p in pairs if p.label != "hallucinated"}
        self.assertEqual(by_src["date"], "ok")
        self.assertEqual(by_src["clock"], "ok")
        self.assertEqual(by_src["precip"], "value_shift")


class PackingTests(unittest.TestCase):
    def test_comma_flush_matches_nltk_peel(self) -> None:
        text = "Aalborg, Viborg, Silkeborg og Herning sender folk."
        tokens = word_tokenize(text)
        self.assertIn(",", tokens)
        chunks = split_long_sentence(text, max_length=20)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(chunks[0].rstrip().endswith(","))

    def test_pack_short_article_is_one_window_at_high_budget(self) -> None:
        article = by_id("bh-04")
        windows = pack_article(article.body_da, budget=400)
        self.assertEqual(len(windows), 1)

    def test_tight_budget_makes_several_windows(self) -> None:
        article = by_id("bh-01")
        windows = pack_article(article.body_da, budget=40)
        self.assertGreaterEqual(len(windows), 3)


class ScarTests(unittest.TestCase):
    def test_echo_is_harmless(self) -> None:
        cases = {c.name: c for c in demo_cases()}
        self.assertTrue(cases["model_echoes_prefix"].harmless)
        self.assertFalse(cases["number_leads_the_summary"].harmless)
        self.assertEqual(cases["number_leads_the_summary"].dropped, "47,2")

    def test_skip_first(self) -> None:
        self.assertEqual(scar_decode(["eng_Latn", "Hello"]), ["Hello"])


if __name__ == "__main__":
    unittest.main()
