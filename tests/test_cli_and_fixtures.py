import json
from pathlib import Path

from fjordpress.cli import main
from fjordpress.corpus import all_articles
from fjordpress.csvio import read_csv
from fjordpress.fixtures import write_fixtures
from fjordpress.ledger import build_ledger, summarise_ledger
from fjordpress.schemas import validate_columns


def test_write_fixtures_match_2023_columns(tmp_path: Path):
    written = write_fixtures(tmp_path, pack_budget=40)
    validate_columns(read_csv(written["raw"])[0].keys(), "raw_input")
    validate_columns(read_csv(written["translated"])[0].keys(), "translated")
    validate_columns(read_csv(written["summarised"])[0].keys(), "summarised")
    validate_columns(read_csv(written["labeled"])[0].keys(), "labeled")
    validate_columns(read_csv(written["train"])[0].keys(), "split")
    validate_columns(read_csv(written["public_eval"])[0].keys(), "public_eval")
    assert len(read_csv(written["raw"])) == len(all_articles())
    assert len(read_csv(written["train"])) == 6
    assert len(read_csv(written["validation"])) == 2
    assert len(read_csv(written["test"])) == 2


def test_ledger_means_are_in_unit_interval():
    from fjordpress.fixtures import hops_for_all

    rows = []
    for rec, art in zip(hops_for_all(), all_articles()):
        rows.extend(build_ledger(rec, art.entities))
    summary = summarise_ledger(rows)
    for key, value in summary.items():
        assert 0.0 <= value <= 1.5, (key, value)
    assert summary["oracle_rouge1"] >= summary["gloss_rouge1"] - 1e-9
    assert summary["oracle_entity_retention"] >= summary["gloss_entity_retention"] - 1e-9


def test_cli_corpus_and_schemas(capsys):
    assert main(["corpus"]) == 0
    out = capsys.readouterr().out
    assert "vk-001" in out
    assert main(["schemas"]) == 0
    assert "article text" in capsys.readouterr().out


def test_cli_lexicon_and_ledger(capsys):
    assert main(["lexicon"]) == 0
    assert "coverage=1.000" in capsys.readouterr().out
    assert main(["ledger"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "oracle_rouge1" in payload


def test_cli_report_and_fixtures(tmp_path: Path, capsys):
    assert main(["fixtures", "--out", str(tmp_path / "data")]) == 0
    assert (tmp_path / "data" / "00_raw_articles.csv").is_file()
    dest = tmp_path / "out"
    assert main(["report", "--out", str(dest)]) == 0
    assert (dest / "vesterklit-lab-notes.html").is_file()
    html = (dest / "vesterklit-lab-notes.html").read_text(encoding="utf-8")
    assert "Fjordpressen" in html
    assert "vk-001" in html
    capsys.readouterr()


def test_cli_counter_and_pack(capsys):
    assert main(["counter", "--text", "Direktør Lisbeth Holm sagde"]) == 0
    out = capsys.readouterr().out
    assert "word tokens" in out
    assert main(["pack", "--budget", "40"]) == 0
    assert "vk-010" in capsys.readouterr().out
