from pathlib import Path

from sejeroe.cli import main

EXPECTED = Path(__file__).resolve().parents[1] / "examples" / "expected_outputs"


def _run(capsys, argv: list[str]) -> str:
    assert main(argv) == 0
    return capsys.readouterr().out


def test_walk_ferry_transcript(capsys) -> None:
    out = _run(capsys, ["walk", "--id", "SEJ-001"])
    assert out == (EXPECTED / "walk_ferry.txt").read_text(encoding="utf-8")


def test_manchet_transcript(capsys) -> None:
    out = _run(capsys, ["manchet", "--id", "SEJ-001"])
    assert out == (EXPECTED / "inspect_manchet_sej001.txt").read_text(encoding="utf-8")


def test_pack_tight_transcript(capsys) -> None:
    out = _run(capsys, ["pack", "--id", "SEJ-001", "--policy", "manchet-tight"])
    assert out == (EXPECTED / "pack_lede_tight.txt").read_text(encoding="utf-8")


def test_length_transcript(capsys) -> None:
    out = _run(capsys, ["length"])
    assert out == (EXPECTED / "length_table.txt").read_text(encoding="utf-8")


def test_baseline_transcript(capsys) -> None:
    out = _run(capsys, ["baseline"])
    assert out == (EXPECTED / "compare_baselines.txt").read_text(encoding="utf-8")


def test_gates_transcript(capsys) -> None:
    out = _run(capsys, ["gates", "--id", "SEJ-001", "--role", "silver_da"])
    assert out == (EXPECTED / "gates_sej001_silver.txt").read_text(encoding="utf-8")


def test_align_transcript(capsys) -> None:
    out = _run(capsys, ["align", "--id", "SEJ-001"])
    assert out == (EXPECTED / "align_sej001.txt").read_text(encoding="utf-8")
