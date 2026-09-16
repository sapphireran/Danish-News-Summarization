from sejeroe.corpus import write_corpus
from sejeroe.csvio import read_header, read_rows
from sejeroe.fixtures import ARTICLES, articles_for_split
from sejeroe.schemas import SCHEMAS, missing_columns
from sejeroe.validate import validate


def test_closed_world_shape() -> None:
    assert len(ARTICLES) == 8
    assert [item.id for item in ARTICLES] == [f"SEJ-{index:03d}" for index in range(1, 9)]
    assert len(articles_for_split("train")) == 5
    assert len(articles_for_split("validation")) == 2
    assert len(articles_for_split("test")) == 1
    assert all(article.quotes for article in ARTICLES)
    assert all(article.planted for article in ARTICLES)


def test_schemas_are_unique() -> None:
    names = [schema.name for schema in SCHEMAS]
    assert len(names) == len(set(names))
    assert missing_columns("labeled_dataset", ["id", "body", "summary"]) == ()
    assert missing_columns("raw_articles", ["id"]) == ("article text",)


def test_write_corpus_headers(tmp_path) -> None:
    written = write_corpus(tmp_path)
    assert "00_raw_articles.csv" in written
    raw = read_rows(written["00_raw_articles.csv"])
    assert [row["id"] for row in raw] == [article.id for article in ARTICLES]
    assert "Sejerøfærgen" in raw[0]["article text"]
    header = read_header(written["05_public_eval_shape.csv"])
    assert header == ["input_text", "target_text", "text_len", "summary_len"]
    labeled = read_rows(written["03_labeled_dataset.csv"])
    assert labeled[0]["summary"].startswith("Færgen til Havnsø")
    problems = validate(tmp_path)
    assert problems == []


def test_train_split_file_has_five_rows(tmp_path) -> None:
    written = write_corpus(tmp_path)
    train = read_rows(written["04_train_dataset.csv"])
    valid = read_rows(written["04_validation_dataset.csv"])
    test = read_rows(written["04_test_dataset.csv"])
    assert len(train) == 5
    assert len(valid) == 2
    assert len(test) == 1
    assert test[0]["id"] == "SEJ-008"
