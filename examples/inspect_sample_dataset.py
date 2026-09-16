#!/usr/bin/env python3
"""Validate the synthetic pipeline CSVs against the documented schema.

Checks, in order:

1. Required columns exist at each hop.
2. Ids are unique inside a file and stay in ``SYN-*`` form.
3. Ids align across the four factory hops (same set, same order optional).
4. Danish letters survive in at least one body.
5. The fine-tune split is a partition of ``sample_labeled_da.csv``.

This is the bookkeeping counterpart to ``run_chunking_demo.py``. It never
downloads a model.

Usage (from repo root):

    python examples/inspect_sample_dataset.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parent / "data"
SPLIT = DATA / "sample_finetune_split"

FACTORY_FILES = {
    "raw": (DATA / "sample_articles.csv", ["id", "article text"]),
    "translated": (DATA / "sample_translated.csv", ["id", "body", "translated"]),
    "summaries_en": (
        DATA / "sample_summaries_en.csv",
        ["id", "body", "translated", "summary"],
    ),
    "labeled_da": (DATA / "sample_labeled_da.csv", ["id", "body", "summary"]),
}

SPLIT_FILES = {
    "train": SPLIT / "train.csv",
    "validation": SPLIT / "validation.csv",
    "test": SPLIT / "test.csv",
}

SYN_PREFIX = "SYN-"
DANISH_LETTERS = set("æøåÆØÅ")


def _fail(message: str) -> None:
    raise SystemExit(f"inspect_sample_dataset: {message}")


def load_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        _fail(f"missing file {path}")
    return pd.read_csv(path, encoding="utf-8")


def check_columns(name: str, df: pd.DataFrame, required: list[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        _fail(f"{name}: missing columns {missing}; have {list(df.columns)}")


def check_ids(name: str, df: pd.DataFrame) -> list[str]:
    if df["id"].isna().any():
        _fail(f"{name}: null id")
    ids = df["id"].astype(str).tolist()
    if len(ids) != len(set(ids)):
        _fail(f"{name}: duplicate ids")
    bad = [i for i in ids if not i.startswith(SYN_PREFIX)]
    if bad:
        _fail(f"{name}: ids must start with {SYN_PREFIX}, got {bad}")
    return ids


def check_danish_letters(name: str, series: pd.Series) -> None:
    blob = "".join(series.fillna("").astype(str).tolist())
    if not DANISH_LETTERS.intersection(blob):
        _fail(f"{name}: expected at least one of æøå in the text")


def check_nonempty(name: str, df: pd.DataFrame, column: str) -> None:
    stripped = df[column].fillna("").astype(str).str.strip()
    if not stripped.astype(bool).all():
        _fail(f"{name}: empty values in {column!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    frames = {}
    id_sets = {}
    for name, (path, cols) in FACTORY_FILES.items():
        df = load_csv(path)
        check_columns(name, df, cols)
        ids = check_ids(name, df)
        id_sets[name] = ids
        frames[name] = df
        print(f"{name:12s}  rows={len(df):2d}  cols={list(df.columns)}")

    base = id_sets["raw"]
    for name, ids in id_sets.items():
        if set(ids) != set(base):
            extra = set(ids) - set(base)
            missing = set(base) - set(ids)
            _fail(
                f"{name}: id set drifted from raw "
                f"(extra={sorted(extra)} missing={sorted(missing)})"
            )

    check_danish_letters("raw", frames["raw"]["article text"])
    check_danish_letters("labeled_da", frames["labeled_da"]["body"])
    check_danish_letters("labeled_da", frames["labeled_da"]["summary"])
    check_nonempty("labeled_da", frames["labeled_da"], "summary")

    # English hop should *not* be required to contain æøå, but bodies stay Danish.
    check_danish_letters("translated.bodies", frames["translated"]["body"])

    split_ids: list[str] = []
    for name, path in SPLIT_FILES.items():
        df = load_csv(path)
        check_columns(name, df, ["id", "body", "summary"])
        ids = check_ids(name, df)
        split_ids.extend(ids)
        print(f"split/{name:10s}  rows={len(df):2d}")

    if len(split_ids) != len(set(split_ids)):
        _fail("fine-tune split: an id appears in more than one split")
    if set(split_ids) != set(base):
        _fail(
            "fine-tune split is not a partition of sample_labeled_da.csv: "
            f"only_in_split={sorted(set(split_ids) - set(base))} "
            f"only_in_labeled={sorted(set(base) - set(split_ids))}"
        )

    print()
    print("alignment: all factory hops share", len(base), "SYN-* ids")
    print("split: train/validation/test partition the labeled set")
    print("danish letters: present in raw bodies and Danish silver summaries")
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
