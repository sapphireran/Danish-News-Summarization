from __future__ import annotations

import csv
from pathlib import Path

from .article import Article
from .corpus import ARTICLES
from .schemas import STAGE_COLUMNS


def write_stage_csv(path: Path, stage: str, articles: tuple[Article, ...] = ARTICLES) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = STAGE_COLUMNS[stage]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for article in articles:
            writer.writerow(_row(stage, article))
    return path


def _row(stage: str, article: Article) -> dict[str, str]:
    if stage == "raw":
        return {"id": article.id, "article text": article.body_da}
    if stage == "translated":
        return {
            "id": article.id,
            "body": article.body_da,
            "translated": article.pivot_en,
        }
    if stage == "summarized":
        return {
            "id": article.id,
            "body": article.body_da,
            "translated": article.pivot_en,
            "summary": article.summary_en,
        }
    if stage in {"labeled", "finetune"}:
        return {
            "id": article.id,
            "body": article.body_da,
            "summary": article.silver_da,
        }
    if stage == "public_eval":
        return {
            "input_text": article.body_da,
            "target_text": article.oracle_da,
            "text_len": str(len(article.body_da.split())),
            "summary_len": str(len(article.oracle_da.split())),
        }
    raise KeyError(stage)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
