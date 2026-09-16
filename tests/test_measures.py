import unittest
from decimal import Decimal

from maalestok.measures import extract_measures, parse_da_number


class ParseNumberTests(unittest.TestCase):
    def test_decimal_comma(self) -> None:
        self.assertEqual(parse_da_number("47,2"), Decimal("47.2"))

    def test_thousands_period(self) -> None:
        self.assertEqual(parse_da_number("3.200"), Decimal("3200"))

    def test_english_thousands_comma(self) -> None:
        self.assertEqual(parse_da_number("3,200"), Decimal("3200"))

    def test_english_decimal(self) -> None:
        self.assertEqual(parse_da_number("47.2"), Decimal("47.2"))

    def test_mixed_danish(self) -> None:
        self.assertEqual(parse_da_number("1.234,56"), Decimal("1234.56"))


class ExtractTests(unittest.TestCase):
    def test_precip_and_clocks(self) -> None:
        text = "I juni faldt 47,2 mm mellem kl. 06.00 og kl. 09.30."
        kinds = [m.kind for m in extract_measures(text)]
        self.assertIn("precip", kinds)
        self.assertGreaterEqual(kinds.count("clock"), 2)

    def test_thousands_is_not_a_clock(self) -> None:
        text = "Afregningen landede på 3.200 kr. pr. ton."
        measures = extract_measures(text)
        self.assertTrue(any(m.kind == "money" and m.value == Decimal("3200") for m in measures))
        self.assertFalse(any(m.kind == "clock" for m in measures))

    def test_signed_temperature(self) -> None:
        text = "Nattemperaturen faldt til −8,3 °C."
        temps = [m for m in extract_measures(text) if m.kind == "temperature"]
        self.assertEqual(len(temps), 1)
        self.assertEqual(temps[0].normalized()[1], Decimal("-8.3"))

    def test_million_kroner(self) -> None:
        text = "Sognerådet har sat 1,2 mio. kr. af."
        money = [m for m in extract_measures(text) if m.kind == "money"]
        self.assertEqual(money[0].normalized()[1], Decimal("1200000"))

    def test_dimension(self) -> None:
        text = "Hallen måler 24 × 44 m inden ombygningen."
        dims = [m for m in extract_measures(text) if m.kind == "dimension"]
        self.assertEqual(len(dims), 1)
        self.assertEqual(dims[0].value, Decimal("24"))
        self.assertEqual(dims[0].extra, "44")

    def test_feast_and_line(self) -> None:
        text = "3. søndag i advent kører linje 82 ikke."
        measures = extract_measures(text)
        self.assertTrue(any(m.kind == "feast" and m.extra == "advent" for m in measures))
        self.assertTrue(any(m.kind == "line" and m.value == Decimal(82) for m in measures))

    def test_percent_and_rate(self) -> None:
        text = "Mælken havde 3,8% fedt, og høsten gav 38 t/ha."
        measures = extract_measures(text)
        self.assertTrue(any(m.kind == "percent" and m.value == Decimal("3.8") for m in measures))
        self.assertTrue(any(m.kind == "yield" and m.unit == "t/ha" for m in measures))

    def test_clock_range(self) -> None:
        text = "Marked varer 09.00–14.00."
        ranges = [m for m in extract_measures(text) if m.kind == "clock_range"]
        self.assertEqual(len(ranges), 1)
        self.assertEqual(ranges[0].extra, "14:00")


if __name__ == "__main__":
    unittest.main()
