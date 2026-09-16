#!/usr/bin/env python3
"""Rewrite example CSV snapshots from ``corpus.py``.

The committed files under ``examples/data/`` should match this exporter.
Tests re-run the writer into a temporary directory and compare headers
and ids with the snapshots so the two copies cannot drift silently.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

from corpus import ARTICLES, articles_for_split  # noqa: E402
from schema import STAGE_FILES, columns_for  # noqa: E402

DATA_DIR = EXAMPLES_DIR / "data"


def _write(path: Path, stage: str, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(columns_for(stage))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row[name] for name in fieldnames})


def build_rows() -> dict[str, list[dict[str, str]]]:
    raw = []
    translated = []
    summarized = []
    labeled = []
    predictions = []
    for article in ARTICLES:
        raw.append({"id": article.id, "article text": article.body_da})
        translated.append(
            {
                "id": article.id,
                "body": article.body_da,
                "translated": article.body_en,
            }
        )
        summarized.append(
            {
                "id": article.id,
                "body": article.body_da,
                "translated": article.body_en,
                "summary": article.summary_en,
            }
        )
        labeled.append(
            {
                "id": article.id,
                "body": article.body_da,
                "summary": article.summary_da,
            }
        )
        predictions.append({"id": article.id, "summary": article.toy_prediction_da})

    splits: dict[str, list[dict[str, str]]] = {}
    for name in ("train", "validation", "test"):
        splits[name] = [
            {
                "id": article.id,
                "body": article.body_da,
                "summary": article.summary_da,
            }
            for article in articles_for_split(name)  # type: ignore[arg-type]
        ]

    return {
        "raw": raw,
        "translated": translated,
        "summarized": summarized,
        "labeled": labeled,
        "predictions": predictions,
        **splits,
    }


def export_all(data_dir: Path = DATA_DIR) -> list[Path]:
    rows_by_stage = build_rows()
    written: list[Path] = []
    mapping = {
        "raw": ("raw", STAGE_FILES["raw"]),
        "translated": ("translated", STAGE_FILES["translated"]),
        "summarized": ("summarized", STAGE_FILES["summarized"]),
        "labeled": ("labeled", STAGE_FILES["labeled"]),
        "predictions": ("predictions", STAGE_FILES["predictions"]),
        "train": ("finetune", STAGE_FILES["train"]),
        "validation": ("finetune", STAGE_FILES["validation"]),
        "test": ("finetune", STAGE_FILES["test"]),
    }
    for key, (stage, filename) in mapping.items():
        path = data_dir / filename
        _write(path, stage, rows_by_stage[key])
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DATA_DIR,
        help="Directory for CSV snapshots (default: examples/data)",
    )
    args = parser.parse_args()
    paths = export_all(args.out_dir)
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
