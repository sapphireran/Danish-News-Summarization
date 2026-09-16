"""Lock the pedagogical overlap numbers so the docs stay honest."""

from __future__ import annotations

from examples.metrics_toy_eval import (
    PAIRS,
    lcs_length,
    lcs_ratio,
    score_all,
    token_f1,
    tokenize,
)


def test_tokenize_strips_punctuation_and_lowercases():
    assert tokenize("Havneby, Havnen!") == ["havneby", "havnen"]


def test_exact_match_is_one():
    scored = {row.name: row for row in score_all()}
    assert scored["exact_match"].token_f1 == 1.0
    assert scored["exact_match"].lcs_ratio == 1.0


def test_unrelated_fluent_is_near_zero():
    scored = {row.name: row for row in score_all()}
    assert scored["unrelated_fluent"].token_f1 < 0.15
    assert scored["unrelated_fluent"].lcs_ratio < 0.15


def test_fact_swap_stays_high():
    """The whole point of the demo: 12 vs 21 barely hurts overlap."""
    scored = {row.name: row for row in score_all()}
    assert scored["fact_swap_budget"].token_f1 >= 0.85
    assert scored["fact_swap_budget"].lcs_ratio >= 0.85


def test_entity_swap_stays_high():
    scored = {row.name: row for row in score_all()}
    assert scored["entity_swap"].token_f1 >= 0.8


def test_close_paraphrase_is_between_unrelated_and_exact():
    scored = {row.name: row for row in score_all()}
    assert (
        scored["unrelated_fluent"].token_f1
        < scored["close_paraphrase"].token_f1
        < scored["exact_match"].token_f1
    )


def test_pair_catalog_has_five_named_cases():
    names = [p.name for p in PAIRS]
    assert names == [
        "exact_match",
        "close_paraphrase",
        "fact_swap_budget",
        "entity_swap",
        "unrelated_fluent",
    ]


def test_lcs_helpers_on_tiny_sequences():
    assert lcs_length(["a", "b", "c"], ["a", "x", "c"]) == 2
    assert lcs_ratio(["a", "b"], ["a", "b"]) == 1.0
    # overlap=2, P=1.0, R=2/3 → F1=0.8
    assert token_f1(["a", "a", "b"], ["a", "b"]) == 0.8
