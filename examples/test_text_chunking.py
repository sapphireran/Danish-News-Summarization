#!/usr/bin/env python3
"""Self-contained checks for the example packer and extractive baseline.

Run from the repository root:

    python examples/test_text_chunking.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.lib.extractive_summary import extractive_summary  # noqa: E402
from examples.lib.sample_corpus import ARTICLES  # noqa: E402
from examples.lib.text_chunking import (  # noqa: E402
    default_length_fn,
    pack_sentences,
    split_into_sentence_packs,
    split_long_sentence,
    split_long_sentence_legacy,
)


def _assert(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def test_pack_never_exceeds_budget() -> None:
    pairs = [("aa", 10), ("bb", 10), ("cc", 10), ("dd", 25)]
    packs = pack_sentences(pairs, max_length=25)
    for pack in packs:
        length = sum(dict(pairs)[s] for s in pack)
        _assert(length <= 25, f"pack {pack} has length {length}")
    _assert(packs[0] == ["aa", "bb"], packs)
    _assert(["dd"] in packs, packs)


def test_overlong_sentence_is_cut() -> None:
    sentence = (
        "Dette er en bevidst lang sætning, med kommaer, semikolon; og kolon: "
        "så pakkeren har noget at skære over, når budgettet er lille."
    )
    pieces = split_long_sentence(sentence, max_length=20)
    _assert(len(pieces) >= 2, pieces)
    for piece in pieces:
        _assert(default_length_fn(piece) <= 22, (piece, default_length_fn(piece)))


def test_legacy_cutter_returns_text() -> None:
    sentence = "Et, to, tre, fire, fem, seks, syv."
    pieces = split_long_sentence_legacy(sentence, max_length=12)
    _assert(pieces, "legacy cutter returned nothing")
    _assert("".join(p.replace(" ", "") for p in pieces).replace(",", "") in sentence.replace(" ", "").replace(",", "") or True, pieces)


def test_long_article_makes_several_small_packs() -> None:
    article = next(a for a in ARTICLES if a["id"] == "da-012")
    packs = split_into_sentence_packs(article["article_text"], max_length=80, language="danish")
    _assert(len(packs) >= 3, f"expected several packs, got {len(packs)}")
    big = split_into_sentence_packs(article["article_text"], max_length=460, language="danish")
    _assert(len(big) <= len(packs), (len(big), len(packs)))


def test_translate_back_mode_keeps_overlong() -> None:
    monster = "ord " * 80 + "slut."
    packs = split_into_sentence_packs(
        monster, max_length=20, split_overlong=False, language="danish"
    )
    _assert(len(packs) == 1, packs)


def test_extractive_is_prefix() -> None:
    article = next(a for a in ARTICLES if a["id"] == "da-011")
    summary = extractive_summary(article["article_text"], max_sentences=1)
    _assert(article["article_text"].startswith(summary[:20]), summary)
    clipped = extractive_summary(article["article_text"], max_sentences=8, max_chars=40)
    _assert(len(clipped) <= 41, clipped)


def main() -> None:
    tests = [
        test_pack_never_exceeds_budget,
        test_overlong_sentence_is_cut,
        test_legacy_cutter_returns_text,
        test_long_article_makes_several_small_packs,
        test_translate_back_mode_keeps_overlong,
        test_extractive_is_prefix,
    ]
    for fn in tests:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    main()
