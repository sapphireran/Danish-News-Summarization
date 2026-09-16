from pathlib import Path

from danish_news_sum.dataset import (
    EVAL_COLUMNS,
    RAW_COLUMNS,
    SILVER_COLUMNS,
    SUMMARIZED_COLUMNS,
    TRANSLATED_COLUMNS,
    load_article_csv,
    summarize_dataset,
    validate_columns,
    window_plan,
)
from danish_news_sum.metrics import lexical_scores

DATA = Path(__file__).resolve().parents[1] / "examples" / "data"

STAGE_FILES = (
    (DATA / "sample_danish_articles.csv", RAW_COLUMNS),
    (DATA / "sample_translated_articles.csv", TRANSLATED_COLUMNS),
    (DATA / "sample_english_summaries.csv", SUMMARIZED_COLUMNS),
    (DATA / "sample_labeled_danish.csv", SILVER_COLUMNS),
    (DATA / "sample_eval_pairs.csv", EVAL_COLUMNS),
)


def test_all_stage_csvs_exist_and_share_ten_aligned_ids():
    ids_per_file = []
    for path, columns in STAGE_FILES:
        assert path.is_file(), path
        rows = load_article_csv(path)
        validate_columns(rows, columns, label=path.name)
        assert len(rows) == 10, path.name
        ids = [row["id"] for row in rows]
        assert len(set(ids)) == 10
        ids_per_file.append(ids)
    first = ids_per_file[0]
    assert all(ids == first for ids in ids_per_file)


def test_labeled_summaries_are_shorter_than_bodies():
    rows = load_article_csv(DATA / "sample_labeled_danish.csv")
    stats = summarize_dataset(rows)
    assert stats.empty_bodies == 0
    assert stats.empty_summaries == 0
    assert stats.mean_compression > 2.0
    assert stats.mean_body_tokens > stats.mean_summary_tokens


def test_eval_pairs_have_nonzero_overlap():
    rows = load_article_csv(DATA / "sample_eval_pairs.csv")
    for row in rows:
        scores = lexical_scores(row["prediction"], row["target_text"], row["input_text"])
        assert scores["rouge1_f1"] > 0.0, row["id"]


def test_danish_articles_pack_into_multiple_windows_at_tight_budget():
    rows = load_article_csv(DATA / "sample_danish_articles.csv")
    plan = window_plan(rows, text_max_length=40)
    assert all(item["window_count"] >= 2 for item in plan)
