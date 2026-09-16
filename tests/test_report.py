import tempfile
import unittest
from pathlib import Path

from kystlinje.align import render_alignment
from kystlinje.corpus import brief_by_id
from kystlinje.report import render_report, write_report


class AlignTests(unittest.TestCase):
    def test_brackets_surviving_tokens(self) -> None:
        brief = brief_by_id("kz-01")
        rendered = render_alignment(brief, hop="silver")
        self.assertIn("[Signe]", rendered)
        self.assertIn("[Brix]", rendered)
        self.assertNotIn("[47]", rendered)


class ReportTests(unittest.TestCase):
    def test_html_contains_telescope_and_briefs(self) -> None:
        html = render_report()
        self.assertIn("Kystlinje entity telescope", html)
        self.assertIn("kz-07", html)
        self.assertIn("mark class", html)
        self.assertIn("Lærke Holm", html)
        self.assertNotIn("10000_articles_without_linebreaks", html)
        self.assertIn("Fiction only", html)

    def test_write_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_report(Path(tmp) / "index.html")
            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 4000)


if __name__ == "__main__":
    unittest.main()
