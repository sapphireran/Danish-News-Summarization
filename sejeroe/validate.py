"""Checks that the closed world is internally consistent."""

from __future__ import annotations

from pathlib import Path

from sejeroe.csvio import read_header
from sejeroe.fixtures import ARTICLES
from sejeroe.normalize import contains_phrase
from sejeroe.paths import DATA_DIR
from sejeroe.schemas import SCHEMAS, missing_columns
from sejeroe.sentences import split_sentences


class ValidationError(Exception):
    pass


def _check_articles() -> list[str]:
    problems: list[str] = []
    seen: set[str] = set()
    splits = {"train": 0, "validation": 0, "test": 0}
    for article in ARTICLES:
        if article.id in seen:
            problems.append(f"duplicate id {article.id}")
        seen.add(article.id)
        if not article.id.startswith("SEJ-"):
            problems.append(f"{article.id}: expected SEJ- prefix")
        splits[article.split] = splits.get(article.split, 0) + 1
        if len(split_sentences(article.body_da)) < 4:
            problems.append(f"{article.id}: Danish body should have at least 4 sentences")
        if not contains_phrase(article.body_da, article.slots.who.split()[-1]):
            problems.append(f"{article.id}: WHO surname missing from Danish body")
        if not article.quotes:
            problems.append(f"{article.id}: missing quote")
        if not article.connectives_da:
            problems.append(f"{article.id}: missing connective list")
        if not article.figures:
            problems.append(f"{article.id}: missing gold figures")
        da_sents = split_sentences(article.body_da)
        en_sents = split_sentences(article.body_en)
        if len(da_sents) != len(en_sents):
            problems.append(
                f"{article.id}: DA/EN sentence counts differ ({len(da_sents)} vs {len(en_sents)})"
            )
        for figure in article.figures:
            if not contains_phrase(article.body_da, figure):
                problems.append(f"{article.id}: figure {figure!r} missing from Danish body")
        for error in article.planted:
            if error.summary_da.strip() == article.summary_da.strip() and error.kind != "quote-loss":
                problems.append(f"{article.id}: planted {error.kind} equals the silver label")
    if splits.get("train", 0) < 1 or splits.get("validation", 0) < 1 or splits.get("test", 0) < 1:
        problems.append(f"expected all three splits, got {splits}")
    return problems


def _check_csv_headers(directory: Path) -> list[str]:
    problems: list[str] = []
    mapping = {
        "raw_articles": "00_raw_articles.csv",
        "translated_articles": "01_translated_articles.csv",
        "summarized_articles": "02_summarized_articles.csv",
        "labeled_dataset": "03_labeled_dataset.csv",
        "finetune_split": "04_train_dataset.csv",
        "public_eval_shape": "05_public_eval_shape.csv",
        "slot_cards": "06_slot_cards.csv",
        "planted_errors": "07_planted_errors.csv",
        "oracle_labels": "03_oracle_labels.csv",
        "figures": "08_figures.csv",
    }
    for schema in SCHEMAS:
        filename = mapping.get(schema.name)
        if not filename:
            continue
        path = directory / filename
        if not path.exists():
            problems.append(f"missing {path.name}")
            continue
        missing = missing_columns(schema.name, read_header(path))
        if missing:
            problems.append(f"{path.name}: missing columns {missing}")
    return problems


def validate(directory: Path | None = None) -> list[str]:
    problems = _check_articles()
    target = directory or DATA_DIR
    if target.exists():
        problems.extend(_check_csv_headers(target))
    return problems


def require_valid(directory: Path | None = None) -> None:
    problems = validate(directory)
    if problems:
        joined = "\n".join(f"- {item}" for item in problems)
        raise ValidationError(f"Sejerø desk fixtures failed validation:\n{joined}")
