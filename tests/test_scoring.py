from __future__ import annotations

from danish_news.scoring import (
    compression_ratio,
    novelty_rate,
    rouge_l,
    rouge_n,
    score_pair,
    tokenize,
)


def test_tokenize_danish_letters() -> None:
    tokens = tokenize("Æbletræet i Århus")
    assert tokens[0] == "æbletræet"
    assert "århus" in tokens


def test_exact_match_is_one() -> None:
    text = "AaB vandt over Randers."
    scores = rouge_n(text, text, n=1)
    assert scores.precision == 1.0
    assert scores.recall == 1.0
    assert scores.f1 == 1.0
    assert rouge_l(text, text).f1 == 1.0


def test_disjoint_is_zero() -> None:
    scores = rouge_n("kat", "hund", n=1)
    assert scores.f1 == 0.0


def test_rouge2_needs_bigrams() -> None:
    pred = "aalborg åbner museet"
    ref = "aalborg åbner havnen"
    r1 = rouge_n(pred, ref, n=1)
    r2 = rouge_n(pred, ref, n=2)
    assert r1.f1 > r2.f1


def test_lcs_partial() -> None:
    scores = rouge_l("a b c d", "a x c d")
    assert scores.f1 > 0.0
    assert scores.f1 < 1.0


def test_compression_and_novelty() -> None:
    source = "Aalborg omdanner den indre havn til et nyt bykvarter med boliger."
    summary = "Aalborg omdanner havnen."
    assert compression_ratio(summary, source) < 1.0
    assert 0.0 <= novelty_rate(summary, source) <= 1.0


def test_score_pair_keys() -> None:
    report = score_pair(
        prediction="Aalborg sender havneplanen i høring.",
        reference="Aalborg sender havneplan i høring.",
        source="Den lange artikel om havnen i Aalborg fortsætter i flere afsnit.",
    )
    payload = report.as_dict()
    assert "rouge1_f1" in payload
    assert "rougeL_f1" in payload
    assert payload["pred_tokens"] > 0
    assert payload["src_tokens"] > payload["pred_tokens"]
