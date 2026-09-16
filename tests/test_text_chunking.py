"""Unit tests for the example packing helpers."""

from __future__ import annotations

import pytest

from examples.text_chunking import (
    WhitespaceTokenizer,
    ensure_nltk,
    pack_sentences,
    sentence_token_lengths,
    split_into_sentence_packs,
    split_long_sentence,
    trace_article,
)


@pytest.fixture(scope="module", autouse=True)
def _nltk_models() -> None:
    ensure_nltk()


def test_whitespace_tokenizer_counts_words_and_special():
    tok = WhitespaceTokenizer()
    assert len(tok.encode("en to tre", add_special_tokens=True)) == 4
    assert len(tok.encode("en to tre", add_special_tokens=False)) == 3
    assert tok.encode("", add_special_tokens=True) == [0]


def test_pack_sentences_greedy_matches_doc_example():
    pairs = [
        ("s1", 8),
        ("s2", 7),
        ("s3", 9),
        ("s4", 4),
    ]
    packs = pack_sentences(pairs, text_max_length=20)
    assert packs == [["s1", "s2"], ["s3", "s4"]]


def test_pack_sentences_oversized_item_gets_its_own_list():
    pairs = [("tiny", 3), ("huge", 50), ("tail", 4)]
    packs = pack_sentences(pairs, text_max_length=10)
    assert packs == [["tiny"], ["huge"], ["tail"]]


def test_split_long_sentence_breaks_on_comma_before_hard_cut():
    # Character budget is small so the comma flush triggers.
    sentence = "alpha, beta, gamma"
    chunks = split_long_sentence(sentence, max_length=10)
    assert len(chunks) >= 2
    assert any("alpha" in chunk for chunk in chunks)


def test_split_into_sentence_packs_on_short_danish():
    article = (
        "Havneby åbner en ny cykelsti. "
        "Kommunen har forhandlet i to år. "
        "Borgmesteren kalder det et løft."
    )
    packs = split_into_sentence_packs(article, text_max_length=8)
    assert len(packs) >= 2
    flat = [sentence for pack in packs for sentence in pack]
    assert any("Havneby" in s for s in flat)
    assert any("Borgmesteren" in s or "løft" in s for s in flat)


def test_trace_article_token_sums_respect_budget_when_pieces_fit():
    tok = WhitespaceTokenizer()
    article = "En kort sætning. Endnu en kort sætning. Og en tredje."
    trace = trace_article("SYN-TEST", article, text_max_length=12, tokenizer=tok)
    assert trace.n_packs >= 1
    for total in trace.pack_token_sums(tok):
        # A single oversized piece may exceed the budget; none of these should.
        assert total <= 12


def test_sentence_token_lengths_keeps_abbreviation_article_in_pieces():
    article = (
        "Projektet koster ca. 2,4 millioner kroner og finansieres bl.a. af en pulje."
    )
    pairs = sentence_token_lengths(
        article, text_max_length=40, tokenizer=WhitespaceTokenizer()
    )
    assert pairs
    blob = " ".join(text for text, _ in pairs)
    assert "millioner" in blob
