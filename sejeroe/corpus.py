"""Project the Sejerø fixtures into the 2023 CSV shapes."""

from __future__ import annotations

from pathlib import Path

from sejeroe.csvio import write_rows
from sejeroe.fixtures import ARTICLES
from sejeroe.models import Article
from sejeroe.paths import DATA_DIR, ensure_output_dirs
from sejeroe.schemas import (
    FIGURE_COLUMNS,
    FINETUNE_COLUMNS,
    LABELED_COLUMNS,
    ORACLE_COLUMNS,
    PLANTED_COLUMNS,
    PUBLIC_EVAL_COLUMNS,
    RAW_COLUMNS,
    SLOT_COLUMNS,
    SUMMARIZED_COLUMNS,
    TRANSLATED_COLUMNS,
)
from sejeroe.tokenize import words


def _raw(article: Article) -> dict[str, object]:
    return {"id": article.id, "article text": article.body_da}


def _translated(article: Article) -> dict[str, object]:
    return {"id": article.id, "body": article.body_da, "translated": article.body_en}


def _summarized(article: Article) -> dict[str, object]:
    return {
        "id": article.id,
        "body": article.body_da,
        "translated": article.body_en,
        "summary": article.summary_en,
    }


def _labeled(article: Article) -> dict[str, object]:
    return {"id": article.id, "body": article.body_da, "summary": article.summary_da}


def _oracle(article: Article) -> dict[str, object]:
    return {
        "id": article.id,
        "body": article.body_da,
        "summary": article.summary_da,
        "oracle": article.oracle_da,
    }


def _slots(article: Article) -> dict[str, object]:
    return {
        "id": article.id,
        "who": article.slots.who,
        "what": article.slots.what,
        "when": article.slots.when,
        "where": article.slots.where,
        "why": article.slots.why,
        "how": article.slots.how,
    }


def _public_eval(article: Article) -> dict[str, object]:
    return {
        "input_text": article.body_da,
        "target_text": article.summary_da,
        "text_len": len(words(article.body_da)),
        "summary_len": len(words(article.summary_da)),
    }


def write_corpus(directory: Path | None = None) -> dict[str, Path]:
    ensure_output_dirs()
    target = directory or DATA_DIR
    target.mkdir(parents=True, exist_ok=True)

    written: dict[str, Path] = {}

    def dump(name: str, columns: tuple[str, ...], rows: list[dict[str, object]]) -> None:
        path = target / name
        write_rows(path, columns, rows)
        written[name] = path

    dump("00_raw_articles.csv", RAW_COLUMNS, [_raw(item) for item in ARTICLES])
    dump("01_translated_articles.csv", TRANSLATED_COLUMNS, [_translated(item) for item in ARTICLES])
    dump("02_summarized_articles.csv", SUMMARIZED_COLUMNS, [_summarized(item) for item in ARTICLES])
    dump("03_labeled_dataset.csv", LABELED_COLUMNS, [_labeled(item) for item in ARTICLES])
    dump("03_oracle_labels.csv", ORACLE_COLUMNS, [_oracle(item) for item in ARTICLES])
    dump("04_train_dataset.csv", FINETUNE_COLUMNS, [_labeled(item) for item in ARTICLES if item.split == "train"])
    dump(
        "04_validation_dataset.csv",
        FINETUNE_COLUMNS,
        [_labeled(item) for item in ARTICLES if item.split == "validation"],
    )
    dump("04_test_dataset.csv", FINETUNE_COLUMNS, [_labeled(item) for item in ARTICLES if item.split == "test"])
    dump("05_public_eval_shape.csv", PUBLIC_EVAL_COLUMNS, [_public_eval(item) for item in ARTICLES])
    dump("06_slot_cards.csv", SLOT_COLUMNS, [_slots(item) for item in ARTICLES])

    planted_rows: list[dict[str, object]] = []
    for article in ARTICLES:
        for error in article.planted:
            planted_rows.append(
                {
                    "id": article.id,
                    "kind": error.kind,
                    "summary": error.summary_da,
                    "dropped_slots": ",".join(error.dropped_slots),
                    "note": error.note,
                }
            )
    dump("07_planted_errors.csv", PLANTED_COLUMNS, planted_rows)
    dump(
        "08_figures.csv",
        FIGURE_COLUMNS,
        [{"id": item.id, "figures": "; ".join(item.figures)} for item in ARTICLES],
    )
    return written
