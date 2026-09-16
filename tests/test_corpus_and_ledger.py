import unittest

from kystlinje.corpus import SPLIT_IDS, all_briefs, brief_by_id
from kystlinje.ledger import build_all_ledgers, build_ledger, hop_loss_table, mean_survival


class CorpusTests(unittest.TestCase):
    def test_eighteen_unique_ids(self) -> None:
        ids = [b.id for b in all_briefs()]
        self.assertEqual(len(ids), 18)
        self.assertEqual(len(set(ids)), 18)
        self.assertTrue(all(i.startswith("kz-") for i in ids))

    def test_split_is_twelve_three_three(self) -> None:
        self.assertEqual(len(SPLIT_IDS["train"]), 12)
        self.assertEqual(len(SPLIT_IDS["validation"]), 3)
        self.assertEqual(len(SPLIT_IDS["test"]), 3)
        self.assertEqual(set(i for v in SPLIT_IDS.values() for i in v), {b.id for b in all_briefs()})

    def test_every_brief_has_all_hops_and_a_scar(self) -> None:
        for brief in all_briefs():
            self.assertTrue(brief.body_da)
            self.assertTrue(brief.pivot_en)
            self.assertTrue(brief.summary_en)
            self.assertTrue(brief.silver_da)
            self.assertGreaterEqual(len(brief.planted), 1)
            self.assertTrue(brief.lead2_da)

    def test_fiction_markers_are_present(self) -> None:
        blob = " ".join(b.body_da for b in all_briefs())
        self.assertIn("Hjelmøerne", blob)
        self.assertIn("Klintø", blob)
        self.assertNotIn("TV2", blob)
        self.assertNotIn("Nordjylland", blob)


class PlantedScarTests(unittest.TestCase):
    def test_hive_count_drifts(self) -> None:
        brief = brief_by_id("kz-05")
        self.assertIn("11", brief.body_da)
        self.assertIn("11", brief.summary_en)
        self.assertIn("12", brief.silver_da)
        self.assertNotIn("12 af 14", brief.body_da)

    def test_year_shift(self) -> None:
        brief = brief_by_id("kz-08")
        self.assertIn("1904", brief.body_da)
        self.assertIn("1904", brief.summary_en)
        self.assertIn("1914", brief.silver_da)

    def test_time_shift(self) -> None:
        brief = brief_by_id("kz-17")
        self.assertIn("23:40", brief.body_da)
        self.assertIn("23:40", brief.summary_en)
        self.assertIn("23:30", brief.silver_da)

    def test_name_stuck(self) -> None:
        brief = brief_by_id("kz-07")
        self.assertIn("Lærke Holm", brief.body_da)
        self.assertIn("Larke Holm", brief.pivot_en)
        self.assertIn("Larke Holm", brief.silver_da)
        self.assertNotIn("Lærke Holm", brief.silver_da)

    def test_hyperbole(self) -> None:
        brief = brief_by_id("kz-02")
        self.assertIn("86", brief.body_da)
        self.assertIn("nearly a hundred", brief.summary_en)
        self.assertIn("næsten hundrede", brief.silver_da)


class LedgerTests(unittest.TestCase):
    def test_source_survival_is_one(self) -> None:
        for led in build_all_ledgers():
            self.assertEqual(led.survival_rate("source"), 1.0)
            self.assertGreaterEqual(len(led.rows), 4)

    def test_kz01_drops_47_in_summary(self) -> None:
        led = build_ledger(brief_by_id("kz-01"))
        forty_seven = next(row for row in led.rows if row.entity.value == "47")
        self.assertTrue(forty_seven.survived("pivot"))
        self.assertFalse(forty_seven.survived("summary"))
        self.assertFalse(forty_seven.survived("silver"))

    def test_kz05_eleven_lost_in_silver(self) -> None:
        led = build_ledger(brief_by_id("kz-05"))
        eleven = next(row for row in led.rows if row.entity.value == "11")
        self.assertTrue(eleven.survived("summary"))
        self.assertFalse(eleven.survived("silver"))

    def test_kz08_year_lost_in_silver(self) -> None:
        led = build_ledger(brief_by_id("kz-08"))
        year = next(row for row in led.rows if row.entity.value == "1904")
        self.assertTrue(year.survived("summary"))
        self.assertFalse(year.survived("silver"))

    def test_kz18_seven_does_not_match_seventy_five(self) -> None:
        led = build_ledger(brief_by_id("kz-18"))
        seven = next(row for row in led.rows if row.entity.value == "7")
        self.assertTrue(seven.survived("source"))
        self.assertFalse(seven.survived("silver"))

    def test_mean_summary_loses_more_than_pivot(self) -> None:
        ledgers = build_all_ledgers()
        self.assertLess(mean_survival(ledgers, "summary"), mean_survival(ledgers, "pivot"))
        loss = {f"{a}->{b}": n for a, b, n in hop_loss_table(ledgers)}
        self.assertGreater(loss["pivot->summary"], loss["source->pivot"])


if __name__ == "__main__":
    unittest.main()
