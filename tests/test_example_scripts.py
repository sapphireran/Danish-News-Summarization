from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def _load(filename: str):
    path = EXAMPLES / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "filename",
    [
        "01_chunk_danish_article.py",
        "02_pipeline_dry_run.py",
        "03_evaluate_toy_summaries.py",
        "04_inspect_csv_schema.py",
        "05_window_budget.py",
        "build_sample_csvs.py",
    ],
)
def test_example_main_help(filename: str) -> None:
    module = _load(filename)
    with pytest.raises(SystemExit) as exit_info:
        module.main(["--help"])
    assert exit_info.value.code == 0


def test_schema_and_eval_examples_succeed(tmp_path) -> None:
    inspect = _load("04_inspect_csv_schema.py")
    evaluate = _load("03_evaluate_toy_summaries.py")
    chunk = _load("01_chunk_danish_article.py")
    budget = _load("05_window_budget.py")
    dry = _load("02_pipeline_dry_run.py")
    assert inspect.main([]) == 0
    assert evaluate.main(["--format", "json"]) == 0
    assert chunk.main(["--article-id", "wx-aarhus", "--max-units", "40"]) == 0
    assert budget.main(["--article-id", "harbour-plan"]) == 0
    assert dry.main(["--output-dir", str(tmp_path)]) == 0
    assert (tmp_path / "labeled_dataset_ml80_rp5.0.csv").is_file()
