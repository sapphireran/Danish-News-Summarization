"""Smoke-test the example CLIs from the repo root."""

from __future__ import annotations

from examples.compare_budgets import main as compare_main
from examples.metrics_toy_eval import main as metrics_main
from examples.run_chunking_demo import main as chunk_main


def test_chunking_demo_syn001(capsys):
    assert chunk_main(["--id", "SYN-001", "--budget", "16"]) == 0
    out = capsys.readouterr().out
    assert "SYN-001" in out
    assert "packs:" in out


def test_chunking_demo_unknown_id() -> None:
    assert chunk_main(["--id", "SYN-999"]) == 2


def test_metrics_cli_table(capsys):
    assert metrics_main([]) == 0
    out = capsys.readouterr().out
    assert "fact_swap_budget" in out
    assert "F1" in out


def test_metrics_cli_json(capsys):
    assert metrics_main(["--json"]) == 0
    out = capsys.readouterr().out
    assert '"name": "exact_match"' in out


def test_compare_budgets_syn004(capsys):
    assert compare_main(["--id", "SYN-004", "--budgets", "16,40,460"]) == 0
    out = capsys.readouterr().out
    assert "budget=16" in out
    assert "budget=40" in out
    assert "budget=460" in out
    assert "packs=1" in out  # production-sized budget fits the sample article
