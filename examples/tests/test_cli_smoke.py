"""Smoke tests for the example CLIs against the committed fixtures."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
DATA = Path(__file__).resolve().parents[1] / "data"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import chunk_text  # noqa: E402
import compute_overlap_metrics  # noqa: E402
import dry_run_pipeline  # noqa: E402
import inspect_dataset  # noqa: E402
import preview_article  # noqa: E402
import split_labeled_dataset  # noqa: E402
import validate_pipeline_config  # noqa: E402


def run_main(func, argv: list[str]) -> int:
    """Call a CLI main() without drowning unittest output."""
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return func(argv)


class InspectSmoke(unittest.TestCase):
    def test_source_fixture_ok(self) -> None:
        code = run_main(
            inspect_dataset.main,
            ["--stage", "source", "--path", str(DATA / "sample_articles.csv"), "--json"],
        )
        self.assertEqual(code, 0)

    def test_remaining_fixtures_ok(self) -> None:
        cases = (
            ("translated", DATA / "sample_translated.csv"),
            ("summarized", DATA / "sample_summarized.csv"),
            ("labeled", DATA / "sample_labeled.csv"),
            ("nordjylland", DATA / "sample_nordjylland_mini.csv"),
        )
        for stage, path in cases:
            with self.subTest(stage=stage):
                self.assertEqual(
                    run_main(inspect_dataset.main, ["--stage", stage, "--path", str(path), "--json"]),
                    0,
                )

    def test_unknown_stage_is_usage_error(self) -> None:
        code = run_main(
            inspect_dataset.main,
            ["--stage", "nope", "--path", str(DATA / "sample_articles.csv")],
        )
        self.assertEqual(code, 2)


class MetricSmoke(unittest.TestCase):
    def test_self_overlap_exit_zero(self) -> None:
        labeled = str(DATA / "sample_labeled.csv")
        code = run_main(
            compute_overlap_metrics.main,
            ["--pred", labeled, "--gold", labeled, "--pred-col", "summary", "--gold-col", "summary"],
        )
        self.assertEqual(code, 0)


class SplitAndDryRun(unittest.TestCase):
    def test_split_writes_three_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code = run_main(
                split_labeled_dataset.main,
                [
                    "--input",
                    str(DATA / "sample_labeled.csv"),
                    "--output-dir",
                    tmp,
                    "--train",
                    "0.7",
                    "--validation",
                    "0.2",
                    "--test",
                    "0.1",
                    "--json",
                ],
            )
            self.assertEqual(code, 0)
            for name in ("train", "validation", "test"):
                self.assertTrue((Path(tmp) / f"{name}_dataset.csv").is_file())

    def test_dry_run_generate_and_replay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generate_dir = Path(tmp) / "gen"
            replay_dir = Path(tmp) / "replay"
            code = run_main(
                dry_run_pipeline.main,
                [
                    "--input",
                    str(DATA / "sample_articles.csv"),
                    "--output-dir",
                    str(generate_dir),
                    "--split",
                    "--json",
                ],
            )
            self.assertEqual(code, 0)
            self.assertTrue((generate_dir / "labeled_dataset_ml80_rp5.0.csv").is_file())
            self.assertTrue((generate_dir / "datasets" / "train_dataset.csv").is_file())
            report = json.loads((generate_dir / "dry_run_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["mode"], "generate")
            self.assertEqual(report["rows"], 10)

            code = run_main(
                dry_run_pipeline.main,
                ["--replay-fixtures", "--output-dir", str(replay_dir), "--json"],
            )
            self.assertEqual(code, 0)
            labeled = (replay_dir / "labeled_dataset_ml80_rp5.0.csv").read_text(encoding="utf-8")
            self.assertIn("Hjørring åbner en fire kilometer", labeled)


class ConfigAndPreview(unittest.TestCase):
    def test_validate_all_example_json(self) -> None:
        self.assertEqual(run_main(validate_pipeline_config.main, ["--all"]), 0)

    def test_preview_lists_and_dumps(self) -> None:
        self.assertEqual(run_main(preview_article.main, ["--list-ids"]), 0)
        self.assertEqual(run_main(preview_article.main, ["--id", "demo-001"]), 0)
        self.assertEqual(run_main(preview_article.main, ["--id", "no-such"]), 2)

    def test_chunk_text_on_source(self) -> None:
        code = run_main(
            chunk_text.main,
            [
                "--path",
                str(DATA / "sample_articles.csv"),
                "--column",
                "article text",
                "--max-tokens",
                "40",
                "--limit",
                "2",
                "--json",
            ],
        )
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
