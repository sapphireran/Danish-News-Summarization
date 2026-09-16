from pathlib import Path

from sejeroe.cli import main
from sejeroe.paths import DATA_DIR, GENERATED_DOCS, REPORT_DIR


def test_help_and_unknown_policy(capsys) -> None:
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()
    assert "manchet desk" in captured.out
    assert main(["pack", "--policy", "not-a-policy"]) == 1


def test_score_and_length_and_planted(capsys) -> None:
    assert main(["score", "--id", "SEJ-001"]) == 0
    out = capsys.readouterr().out
    assert "SEJ-001" in out
    assert "slots=" in out
    assert main(["length"]) == 0
    length_out = capsys.readouterr().out
    assert "SEJ-008" in length_out
    assert main(["planted"]) == 0
    planted = capsys.readouterr().out
    assert "who-swap" in planted
    assert "polarity-flip" in planted
    assert main(["baseline"]) == 0
    baseline = capsys.readouterr().out
    assert "lead1_m" in baseline
    assert "SEJ-001" in baseline
    assert main(["gates", "--id", "SEJ-001", "--role", "silver_da"]) == 0
    gates = capsys.readouterr().out
    assert "quote_or_speaker" in gates
    assert main(["align", "--id", "SEJ-001"]) == 0
    aligned = capsys.readouterr().out
    assert "aligned=True" in aligned
    assert "quote" in aligned


def test_all_writes_artifacts(tmp_path, capsys, monkeypatch) -> None:
    # Keep the committed examples/data intact; write a side copy then run report.
    assert main(["hops", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "00_raw_articles.csv").exists()
    assert main(["validate", "--out", str(tmp_path)]) == 0
    assert main(["report"]) == 0
    assert (GENERATED_DOCS / "desk-notes.txt").exists()
    assert (REPORT_DIR / "index.html").exists()
    notes = Path(GENERATED_DOCS / "desk-notes.txt").read_text(encoding="utf-8")
    assert "Sejerø Tidende" in notes
    assert "SEJ-001" in notes
    html = (REPORT_DIR / "index.html").read_text(encoding="utf-8")
    assert "slot recall" in html
    assert "Extractive lead-1" in html
    assert main(["cards"]) == 0
    assert (GENERATED_DOCS / "cards" / "SEJ-001.md").exists()
    assert DATA_DIR.joinpath("08_figures.csv").exists() or DATA_DIR.joinpath("07_planted_errors.csv").exists()
    capsys.readouterr()
