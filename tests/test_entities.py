import unittest

from kystlinje.entities import entity_survives, extract_entities, unique_by_key


class GazetteerTests(unittest.TestCase):
    def test_longest_org_wins_over_place(self) -> None:
        text = "Hjelmhøj Messingorkester spiller i Hjelmhøj."
        keys = [e.key for e in unique_by_key(extract_entities(text))]
        self.assertIn("org:messing", keys)
        self.assertIn("place:hjelmhoj", keys)

    def test_person_and_place(self) -> None:
        text = "Lærke Holm optog bånd i Sognehavn Læsehus."
        keys = {e.key for e in extract_entities(text)}
        self.assertIn("person:laerke-holm", keys)
        self.assertIn("org:laesehus", keys)

    def test_english_alias_counts_as_survival(self) -> None:
        ents = extract_entities("Klintø Skakklub holdt finale.")
        club = next(e for e in ents if e.key == "org:skakklub")
        self.assertTrue(entity_survives(club, "Klintø Chess Club won on Saturday."))


class NumberTests(unittest.TestCase):
    def test_time_and_year(self) -> None:
        text = "Slusen fra 1904 lukker kl. 23:40."
        ents = extract_entities(text, article_id="kz-x")
        kinds = {e.kind for e in ents}
        self.assertIn("year", kinds)
        self.assertIn("time", kinds)

    def test_money(self) -> None:
        text = "Billetten koster 40 kr. i kassen."
        ents = extract_entities(text, article_id="kz-x")
        self.assertTrue(any(e.kind == "money" and e.value == "40" for e in ents))

    def test_number_does_not_survive_hyperbole(self) -> None:
        ents = extract_entities("De podede 86 træer.", article_id="kz-02")
        eighty_six = next(e for e in ents if e.value == "86")
        self.assertFalse(entity_survives(eighty_six, "They grafted nearly a hundred trees."))
        self.assertTrue(entity_survives(eighty_six, "They grafted 86 old trees."))


class CompoundTests(unittest.TestCase):
    def test_blaeretang(self) -> None:
        ents = extract_entities("Ordet for blæretang skifter.")
        self.assertTrue(any(e.key == "compound:blæretang" for e in ents))


if __name__ == "__main__":
    unittest.main()
