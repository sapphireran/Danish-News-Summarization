#!/usr/bin/env python3
"""Self-checks for the portable packer (stdlib only).

    python examples/test_text_chunking.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from text_chunking import (  # noqa: E402
    pack_article,
    pack_sentences,
    simple_sent_tokenize,
    split_long_sentence_char_budget,
    split_long_sentence_token_budget,
    whitespace_tokenizer_len,
    word_tokenize,
)


def _assert(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def test_sentence_split_basic() -> None:
    text = "Første sætning. Anden sætning! Tredje sætning?"
    sentences = simple_sent_tokenize(text)
    _assert(sentences == ["Første sætning.", "Anden sætning!", "Tredje sætning?"], sentences)


def test_abbreviation_not_split() -> None:
    text = "Kommunen nævner bl.a. cykelstier og f.eks. fartvisere. Det er alt."
    sentences = simple_sent_tokenize(text)
    _assert(len(sentences) == 2, sentences)
    _assert(sentences[0].startswith("Kommunen"), sentences)


def test_pack_respects_budget() -> None:
    sentences = [
        "En kort sætning her.",
        "Endnu en kort sætning.",
        "Og en tredje sætning til sidst.",
    ]
    packed = pack_sentences(sentences, text_max_length=8, tokenizer_len=whitespace_tokenizer_len)
    _assert(packed.pack_count >= 2, packed)
    for length in packed.token_lengths:
        _assert(length <= 8, (length, packed))


def test_empty_article() -> None:
    packed = pack_article("   ", text_max_length=40)
    _assert(packed.pack_count == 0, packed)


def test_word_tokenize_keeps_commas() -> None:
    tokens = word_tokenize("Hej, verden.")
    _assert("," in tokens and "." in tokens, tokens)


def test_char_splitter_cuts_long_string() -> None:
    # A comma-separated list longer than a tiny budget.
    sentence = ", ".join([f"ord{i}" for i in range(20)])
    chunks = split_long_sentence_char_budget(sentence, max_length=25)
    _assert(len(chunks) > 1, chunks)
    _assert("".join(c.replace(" ", "") for c in chunks).replace(",", "") != "", chunks)


def test_token_splitter_uses_word_counts() -> None:
    sentence = "alpha, beta, gamma, delta, epsilon, zeta, eta, theta"
    chunks = split_long_sentence_token_budget(
        sentence, max_length=4, tokenizer_len=whitespace_tokenizer_len
    )
    _assert(len(chunks) > 1, chunks)
    for chunk in chunks:
        _assert(whitespace_tokenizer_len(chunk) <= 4, (chunk, chunks))


def test_roundtrip_join() -> None:
    text = "København åbner en sti. Aarhus holder festuge."
    packed = pack_article(text, text_max_length=40)
    joined = " ".join(packed.as_texts())
    _assert("København" in joined and "Aarhus" in joined, joined)


def main() -> int:
    tests = [
        test_sentence_split_basic,
        test_abbreviation_not_split,
        test_pack_respects_budget,
        test_empty_article,
        test_word_tokenize_keeps_commas,
        test_char_splitter_cuts_long_string,
        test_token_splitter_uses_word_counts,
        test_roundtrip_join,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"ok  {test.__name__}")
        except Exception as exc:  # noqa: BLE001 — show the failing check
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
