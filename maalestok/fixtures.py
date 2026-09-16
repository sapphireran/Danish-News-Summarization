"""Write course-shaped CSVs and a planted-error table under examples/data."""

from __future__ import annotations

import csv
from pathlib import Path

from .corpus import ARTICLES
from .csvio import write_stage_csv
from .paths import DATA_DIR
from .schemas import STAGE_COLUMNS

SPLIT = {
    "train": tuple(article.id for article in ARTICLES[:10]),
    "validation": tuple(article.id for article in ARTICLES[10:13]),
    "test": tuple(article.id for article in ARTICLES[13:]),
}


def write_all(data_dir: Path = DATA_DIR) -> dict[str, Path]:
    data_dir.mkdir(parents=True, exist_ok=True)
    written = {
        "raw": write_stage_csv(data_dir / "00_raw_articles.csv", "raw"),
        "translated": write_stage_csv(data_dir / "01_translated_articles.csv", "translated"),
        "summarized": write_stage_csv(data_dir / "02_summarized_articles.csv", "summarized"),
        "labeled": write_stage_csv(data_dir / "03_labeled_dataset.csv", "labeled"),
        "oracle": _write_oracle(data_dir / "03_labeled_oracle.csv"),
        "public_eval": write_stage_csv(data_dir / "05_public_eval_shape.csv", "public_eval"),
        "planted": _write_planted(data_dir / "planted_errors.csv"),
    }
    for split_name, ids in SPLIT.items():
        subset = tuple(article for article in ARTICLES if article.id in ids)
        written[split_name] = write_stage_csv(
            data_dir / f"04_{split_name}_dataset.csv",
            "finetune",
            subset,
        )
    return written


def _write_oracle(path: Path) -> Path:
    columns = STAGE_COLUMNS["labeled"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for article in ARTICLES:
            writer.writerow(
                {
                    "id": article.id,
                    "body": article.body_da,
                    "summary": article.oracle_da,
                }
            )
    return path


def _write_planted(path: Path) -> Path:
    columns = ("id", "code", "hop", "source_raw", "silver_raw", "note")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for article in ARTICLES:
            for err in article.planted:
                writer.writerow(
                    {
                        "id": article.id,
                        "code": err.code,
                        "hop": err.hop,
                        "source_raw": err.source_raw,
                        "silver_raw": err.silver_raw,
                        "note": err.note,
                    }
                )
    return path
