"""Schema and content checks for the synthetic example CSVs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from examples.inspect_sample_dataset import (
    DANISH_LETTERS,
    FACTORY_FILES,
    SPLIT_FILES,
    SYN_PREFIX,
)
from examples.text_chunking import ensure_nltk, split_into_sentence_packs

DATA = Path(__file__).resolve().parents[1] / "examples" / "data"


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")


def test_factory_files_exist_and_have_eight_rows():
    for name, (path, cols) in FACTORY_FILES.items():
        df = _read(path)
        assert len(df) == 8, name
        for col in cols:
            assert col in df.columns, (name, col)


def test_all_ids_are_syn_and_unique():
    raw = _read(DATA / "sample_articles.csv")
    ids = raw["id"].astype(str).tolist()
    assert ids == [f"SYN-{i:03d}" for i in range(1, 9)]
    labeled = _read(DATA / "sample_labeled_da.csv")
    assert set(labeled["id"].astype(str)) == set(ids)


def test_bodies_are_identical_across_hops():
    raw = _read(DATA / "sample_articles.csv")
    translated = _read(DATA / "sample_translated.csv")
    summaries = _read(DATA / "sample_summaries_en.csv")
    labeled = _read(DATA / "sample_labeled_da.csv")

    raw_map = dict(zip(raw["id"].astype(str), raw["article text"].astype(str)))
    for df in (translated, summaries, labeled):
        for _, row in df.iterrows():
            assert row["body"] == raw_map[str(row["id"])]


def test_english_hop_is_not_identical_to_danish_body():
    translated = _read(DATA / "sample_translated.csv")
    for _, row in translated.iterrows():
        assert row["translated"] != row["body"]
        # Crude language check: English hop should contain common English words.
        assert any(
            word in row["translated"].lower()
            for word in ("the", "a", "and", "is", "to")
        )


def test_danish_letters_present():
    raw = _read(DATA / "sample_articles.csv")
    blob = "".join(raw["article text"].astype(str).tolist())
    assert DANISH_LETTERS.intersection(blob)
    labeled = _read(DATA / "sample_labeled_da.csv")
    sum_blob = "".join(labeled["summary"].astype(str).tolist())
    assert DANISH_LETTERS.intersection(sum_blob)


def test_no_http_or_outlet_bylines():
    """Guardrail: sample fiction should not look scraped."""
    raw = _read(DATA / "sample_articles.csv")
    blob = " ".join(raw["article text"].astype(str).tolist()).lower()
    for banned in ("http://", "https://", "copyright", "ritzau", "©"):
        assert banned not in blob


def test_ids_use_syn_prefix_constant():
    assert SYN_PREFIX == "SYN-"


def test_finetune_split_is_partition():
    labeled = set(_read(DATA / "sample_labeled_da.csv")["id"].astype(str))
    seen = []
    expected_counts = {"train": 5, "validation": 2, "test": 1}
    for name, path in SPLIT_FILES.items():
        ids = _read(path)["id"].astype(str).tolist()
        assert len(ids) == expected_counts[name], name
        seen.extend(ids)
    assert len(seen) == len(set(seen))
    assert set(seen) == labeled


def test_split_summaries_match_labeled_file():
    labeled_df = _read(DATA / "sample_labeled_da.csv")
    labeled = labeled_df.set_index(labeled_df["id"].astype(str), drop=False)
    for path in SPLIT_FILES.values():
        df = _read(path)
        for _, row in df.iterrows():
            gold = labeled.loc[str(row["id"])]
            assert row["summary"] == gold["summary"]
            assert row["body"] == gold["body"]


def test_syn004_is_long_enough_to_pack_under_demo_budget():
    ensure_nltk()
    raw = _read(DATA / "sample_articles.csv")
    body = raw.loc[raw["id"] == "SYN-004", "article text"].iloc[0]
    packs = split_into_sentence_packs(body, text_max_length=16)
    assert len(packs) >= 3


def test_inspect_script_main_returns_zero(capsys):
    from examples.inspect_sample_dataset import main

    assert main([]) == 0
    out = capsys.readouterr().out
    assert "ok" in out
    assert "SYN-" not in out or "alignment" in out
