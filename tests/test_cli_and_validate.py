import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from kystlinje.exercises import grade, questions
from kystlinje.schemas import COURSE_SCHEMAS
from kystlinje.tables import write_all_tables
from kystlinje.validate import run_checks, summary


ROOT = Path(__file__).resolve().parent.parent


class SchemaTests(unittest.TestCase):
    def test_article_text_space(self) -> None:
        source = next(s for s in COURSE_SCHEMAS if s.name == "source-articles")
        self.assertEqual(source.columns, ("id", "article text"))

    def test_labeled_drops_english(self) -> None:
        labeled = next(s for s in COURSE_SCHEMAS if s.name == "labeled")
        self.assertEqual(labeled.columns, ("id", "body", "summary"))


class ValidateTests(unittest.TestCase):
    def test_all_checks_pass(self) -> None:
        checks = run_checks()
        failed = [c.name for c in checks if not c.ok]
        self.assertEqual(failed, [], msg=f"failed: {failed}")
        ok, total = summary(checks)
        self.assertEqual(ok, total)
        self.assertGreaterEqual(total, 40)


class ExerciseTests(unittest.TestCase):
    def test_ten_questions(self) -> None:
        qs = questions()
        self.assertEqual(len(qs), 10)
        for q in qs:
            ok, expected = grade(q.number, q.answer)
            self.assertTrue(ok, msg=f"Q{q.number} self-grade failed (expected {expected})")

    def test_wrong_answer(self) -> None:
        ok, _ = grade(6, "0")
        self.assertFalse(ok)


class TableTests(unittest.TestCase):
    def test_write_tables_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_all_tables(Path(tmp))
            names = {p.name for p in paths}
            self.assertIn("kystlinje_articles.csv", names)
            header = (Path(tmp) / "kystlinje_articles.csv").read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(header, "id,article text")
            labeled = (Path(tmp) / "kystlinje_labeled.csv").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(labeled), 19)  # header + 18
            train = (Path(tmp) / "kystlinje_train.csv").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(train), 13)


class CliTests(unittest.TestCase):
    def test_list_and_validate(self) -> None:
        listed = subprocess.run(
            [sys.executable, "-m", "kystlinje", "list"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("kz-01", listed.stdout)
        self.assertIn("kz-18", listed.stdout)
        validated = subprocess.run(
            [sys.executable, "-m", "kystlinje", "validate", "--quiet"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("checks passed", validated.stdout)

    def test_quiz_grade_accepts_live_answer(self) -> None:
        q6 = next(q for q in questions() if q.number == 6)
        graded = subprocess.run(
            [sys.executable, "-m", "kystlinje", "quiz", "--grade", "6", q6.answer],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("ok", graded.stdout)


if __name__ == "__main__":
    unittest.main()
