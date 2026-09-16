import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.support import REPO_ROOT


def _run(script: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "examples" / script), *args],
        cwd=cwd or REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class CliSmokeTests(unittest.TestCase):
    def test_validate_schema_passes_on_fixtures(self) -> None:
        proc = _run("validate_schema.py")
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("all schema checks passed", proc.stdout)

    def test_inspect_samples_prints_header(self) -> None:
        proc = _run("inspect_samples.py")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("klintelund-cykelsti", proc.stdout)
        self.assertIn("oesterhavn-kvote", proc.stdout)

    def test_compare_hops_single_id(self) -> None:
        proc = _run("compare_hops.py", "--id", "lund-bageri")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("lund-bageri", proc.stdout)
        self.assertIn("silver", proc.stdout)
        self.assertIn("Bageriet Lund", proc.stdout)

    def test_pack_report_long_row(self) -> None:
        proc = _run("pack_report.py", "--id", "oesterhavn-kvote", "--budget", "20")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("oesterhavn-kvote", proc.stdout)
        self.assertIn("group", proc.stdout)

    def test_toy_pipeline_writes_four_csvs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run("run_toy_pipeline.py", "--output", tmp, "--budget", "40")
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
            out = Path(tmp)
            for name in (
                "toy_articles.csv",
                "toy_translated.csv",
                "toy_summaries_en.csv",
                "toy_labeled.csv",
            ):
                self.assertTrue((out / name).is_file(), msg=name)
            self.assertIn("klintelund-cykelsti", proc.stdout)
            self.assertIn("wrote:", proc.stdout)

    def test_unknown_compare_id_is_exit_2(self) -> None:
        proc = _run("compare_hops.py", "--id", "does-not-exist")
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
