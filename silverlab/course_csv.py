"""Write the fictional briefs using the 2023 `article text` header.

This is only a column-contract helper. It does not invent the missing 10k dump.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .fiction import REPO_ROOT, load_briefs

DEFAULT_CSV = REPO_ROOT / "examples" / "data" / "fiction_articles.csv"
ARTICLE_HEADER = "article text"


def write_articles_csv(path: Path | None = None) -> Path:
    target = path or DEFAULT_CSV
    target.parent.mkdir(parents=True, exist_ok=True)
    briefs = load_briefs()
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", ARTICLE_HEADER, "title", "topic"])
        writer.writeheader()
        for brief in briefs:
            writer.writerow(
                {
                    "id": brief.id,
                    ARTICLE_HEADER: brief.article_text,
                    "title": brief.title,
                    "topic": brief.topic,
                }
            )
    return target
