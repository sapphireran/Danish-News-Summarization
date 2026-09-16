"""Keep frozen demo transcripts in sync with the CLIs."""

from __future__ import annotations

from pathlib import Path

from examples.compare_budgets import main as compare_main
from examples.inspect_sample_dataset import main as inspect_main
from examples.metrics_toy_eval import main as metrics_main
from examples.run_chunking_demo import main as chunk_main

EXPECTED = Path(__file__).resolve().parents[1] / "examples" / "expected_outputs"


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n").rstrip() + "\n"


def test_chunking_demo_matches_frozen_stdout(capsys):
    assert chunk_main(["--id", "SYN-001", "--id", "SYN-004"]) == 0
    actual = _normalize(capsys.readouterr().out)
    frozen = _normalize(
        (EXPECTED / "chunking_demo_syn001_syn004.txt").read_text(encoding="utf-8")
    )
    assert actual == frozen


def test_compare_budgets_matches_frozen_stdout(capsys):
    assert compare_main(["--id", "SYN-004"]) == 0
    actual = _normalize(capsys.readouterr().out)
    frozen = _normalize(
        (EXPECTED / "compare_budgets_syn004.txt").read_text(encoding="utf-8")
    )
    assert actual == frozen


def test_metrics_matches_frozen_stdout(capsys):
    assert metrics_main([]) == 0
    actual = _normalize(capsys.readouterr().out)
    frozen = _normalize((EXPECTED / "metrics_toy_eval.txt").read_text(encoding="utf-8"))
    assert actual == frozen


def test_inspect_matches_frozen_stdout(capsys):
    assert inspect_main([]) == 0
    actual = _normalize(capsys.readouterr().out)
    frozen = _normalize(
        (EXPECTED / "inspect_sample_dataset.txt").read_text(encoding="utf-8")
    )
    assert actual == frozen
