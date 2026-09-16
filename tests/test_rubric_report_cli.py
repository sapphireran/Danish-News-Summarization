import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from silverlab.cli import main
from silverlab.report import build_report_html, write_report
from silverlab.rubric import score_rubric
from silverlab.tables import format_table


class RubricTests(unittest.TestCase):
    def test_empty_summary_is_floor(self) -> None:
        scores = score_rubric("Der er kaffe i teltet.", "")
        self.assertEqual(scores.faithfulness, 1)
        self.assertEqual(scores.notes, "empty summary")

    def test_supported_danish_summary_scores_high_faithfulness(self) -> None:
        article = "Himmerlands Observatorium åbner lørdag aften og viser Saturn."
        summary = "Observatorium åbner lørdag og viser Saturn."
        scores = score_rubric(article, summary, summary)
        self.assertGreaterEqual(scores.faithfulness, 4)
        self.assertGreaterEqual(scores.danish_naturalness, 3)

    def test_english_leftover_hurts_naturalness(self) -> None:
        article = "Radio Thy sender fra et telt på torvet i Thisted."
        clean = "Radio Thy sender fra et telt i Thisted."
        dirty = "Radio Thy sender from a tent on the square i Thisted."
        clean_scores = score_rubric(article, clean)
        dirty_scores = score_rubric(article, dirty)
        self.assertLess(dirty_scores.danish_naturalness, clean_scores.danish_naturalness)
        self.assertIn("English leftover", dirty_scores.notes)


class ReportTests(unittest.TestCase):
    def test_html_contains_expected_anchors(self) -> None:
        html = build_report_html()
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("id='lab-01'", html)
        self.assertIn('id="means"', html)
        self.assertIn('id="catalog"', html)
        self.assertIn("err-02", html)
        self.assertIn("ROUGE-1", html)
        self.assertNotIn("0.999", html)  # do not invent a perfect 2023 scoreboard

    def test_write_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.html"
            write_report(path)
            text = path.read_text(encoding="utf-8")
            self.assertGreater(len(text), 2000)
            self.assertIn("lab-16", text)


class TableTests(unittest.TestCase):
    def test_format_table_aligns(self) -> None:
        table = format_table(("id", "n"), [("lab-01", "6"), ("x", "10")])
        lines = table.splitlines()
        self.assertEqual(len(lines), 4)
        self.assertTrue(lines[1].startswith("|-"))
        self.assertIn("lab-01", lines[2])


class CliTests(unittest.TestCase):
    def _run(self, argv: list[str]) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(argv)
        return code, buf.getvalue()

    def test_list(self) -> None:
        code, out = self._run(["list"])
        self.assertEqual(code, 0)
        self.assertIn("lab-01", out)
        self.assertIn("lab-16", out)

    def test_baselines_single(self) -> None:
        code, out = self._run(["baselines", "--id", "lab-01"])
        self.assertEqual(code, 0)
        self.assertIn("lead1", out)
        self.assertIn("textrank", out)

    def test_baselines_unknown(self) -> None:
        code, _ = self._run(["baselines", "--id", "nope"])
        self.assertEqual(code, 2)

    def test_metrics(self) -> None:
        code, out = self._run(["metrics", "--against", "extractive"])
        self.assertEqual(code, 0)
        self.assertIn("lead1", out)
        self.assertIn("R1 F", out)

    def test_catalog_and_rubric(self) -> None:
        code, out = self._run(["catalog"])
        self.assertEqual(code, 0)
        self.assertIn("HOP-TR", out)
        self.assertIn("err-01", out)
        code, out = self._run(["rubric", "--id", "lab-03"])
        self.assertEqual(code, 0)
        self.assertIn("lab-03", out)

    def test_validate(self) -> None:
        code, out = self._run(["validate"])
        self.assertEqual(code, 0)
        self.assertIn("passed", out)

    def test_report_and_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "report.html"
            code, out = self._run(["report", "--out", str(html_path)])
            self.assertEqual(code, 0)
            self.assertTrue(html_path.is_file())
            self.assertIn("wrote", out)
