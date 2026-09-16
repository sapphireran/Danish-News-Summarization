from __future__ import annotations

from pathlib import Path

from danish_news.config import load_config
from danish_news.schemas import read_csv
from examples.data.corpus import ARTICLES, by_id


def test_config_points_at_example_data() -> None:
    config = load_config()
    assert config.resolve("raw_csv").name == "sample_articles.csv"
    assert config.max_units == 80


def test_committed_csvs_match_corpus() -> None:
    root = Path(__file__).resolve().parents[1] / "examples" / "data"
    raw = {row["id"]: row for row in read_csv(root / "sample_articles.csv", "raw")}
    labeled = {row["id"]: row for row in read_csv(root / "sample_labeled.csv", "labeled")}
    references = {
        row["id"]: row for row in read_csv(root / "sample_references.csv", "labeled")
    }
    catalog = by_id()
    assert set(raw) == set(catalog)
    for article in ARTICLES:
        assert raw[article["id"]]["article text"] == article["article_text"]
        assert labeled[article["id"]]["summary"] == article["summary_da"]
        assert references[article["id"]]["summary"] == article["reference_da"]
        # Silver and reference headlines are not supposed to be identical;
        # the toy evaluator exists because they differ.
        assert labeled[article["id"]]["summary"] != article["reference_da"]
