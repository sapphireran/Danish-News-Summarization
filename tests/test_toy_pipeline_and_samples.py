from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
SAMPLE_DATA = _EXAMPLES / "sample_data"
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))

from build_sample_data import build
from csv_util import read_rows
from sample_articles import ARTICLES, by_id, ids
from schema import SAMPLE_FILENAMES, STAGE_0_ARTICLES, STAGE_3_LABELED
from toy_pipeline import mock_summarize_en, mock_translate_da_en, run_pipeline
from validate_csvs import validate_alignment, validate_file


class SampleArticleTests(unittest.TestCase):
    def test_twelve_unique_ids(self) -> None:
        article_ids = ids()
        self.assertEqual(len(article_ids), 12)
        self.assertEqual(len(set(article_ids)), 12)
        self.assertTrue(all(item.startswith("dn-") for item in article_ids))

    def test_every_article_has_all_fields(self) -> None:
        for item in ARTICLES:
            self.assertGreater(len(item["article_text"]), 80, item["id"])
            self.assertGreater(len(item["translated"]), 80, item["id"])
            self.assertGreater(len(item["summary_en"]), 20, item["id"])
            self.assertGreater(len(item["summary_da"]), 20, item["id"])
            self.assertNotEqual(item["article_text"], item["translated"], item["id"])

    def test_by_id_lookup_and_unknown(self) -> None:
        self.assertEqual(by_id("dn-004")["id"], "dn-004")
        with self.assertRaises(KeyError):
            by_id("dn-999")


class ToyPipelineTests(unittest.TestCase):
    def test_mock_translate_is_prefixed(self) -> None:
        self.assertEqual(mock_translate_da_en("hej"), "[EN] hej")

    def test_mock_summarize_returns_text(self) -> None:
        english = "[EN] Første sætning. Anden sætning. Tredje sætning."
        summary = mock_summarize_en(english, text_max_length=400)
        self.assertTrue(summary)
        self.assertIn("Første", summary)

    def test_mock_pipeline_writes_valid_csvs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            written = run_pipeline(
                stage0_path=SAMPLE_DATA / SAMPLE_FILENAMES[STAGE_0_ARTICLES],
                output_dir=Path(tmp),
                text_max_length=180,
                replay_gold=False,
            )
            issues = []
            staged = {STAGE_0_ARTICLES: SAMPLE_DATA / SAMPLE_FILENAMES[STAGE_0_ARTICLES]}
            for stage, path in written.items():
                issues.extend(validate_file(path, stage))
                staged[stage] = path
            issues.extend(validate_alignment(staged))
            self.assertEqual(issues, [], msg="\n".join(str(issue) for issue in issues))

    def test_replay_gold_matches_sample_articles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            written = run_pipeline(
                stage0_path=SAMPLE_DATA / SAMPLE_FILENAMES[STAGE_0_ARTICLES],
                output_dir=Path(tmp),
                text_max_length=460,
                replay_gold=True,
            )
            _header, labeled = read_rows(written[STAGE_3_LABELED])
            gold = {item["id"]: item["summary_da"] for item in ARTICLES}
            for row in labeled:
                self.assertEqual(row["summary"], gold[row["id"]])


class RebuildRoundTripTests(unittest.TestCase):
    def test_builder_matches_committed_sample_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            built = build(Path(tmp))
            for name, path in built.items():
                committed = SAMPLE_DATA / path.name
                self.assertTrue(committed.exists(), f"missing committed {path.name}")
                self.assertEqual(
                    path.read_text(encoding="utf-8"),
                    committed.read_text(encoding="utf-8"),
                    msg=f"drift in {name}: {path.name}",
                )


if __name__ == "__main__":
    unittest.main()
