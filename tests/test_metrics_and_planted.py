from sejeroe.fixtures import ARTICLES, article_by_id
from sejeroe.metrics import overlap, planted_blind_spots, score_article, score_text


def test_overlap_is_one_on_identical_text() -> None:
    text = "Færgen til Havnsø er aflyst i eftermiddag."
    score = overlap(text, text)
    assert score.rouge1_f == 1.0
    assert score.rouge2_f == 1.0
    assert score.rougel_f == 1.0


def test_overlap_is_zero_on_disjoint_text() -> None:
    score = overlap("abc def", "xyz uvw")
    assert score.rouge1_f == 0.0


def test_who_swap_keeps_high_unigram_overlap() -> None:
    article = article_by_id("SEJ-001")
    row = next(item for item in planted_blind_spots(article) if item["kind"] == "who-swap")
    assert row["planted_rouge1_vs_silver"] >= 0.7
    assert row["planted_slot_recall"] < row["silver_slot_recall"]


def test_polarity_flip_is_a_slot_miss_not_just_noise() -> None:
    article = article_by_id("SEJ-005")
    planted = next(item for item in article.planted if item.kind == "polarity-flip")
    row = score_text(article, planted.summary_da, "planted:polarity-flip")
    assert "what" in row.missing_slots or "why" in row.missing_slots
    assert row.rouge1_vs_silver >= 0.45


def test_every_article_has_silver_and_oracle_rows() -> None:
    for article in ARTICLES:
        roles = {row.text_role for row in score_article(article)}
        assert "summary_da" in roles
        assert "oracle_da" in roles
        assert any(role.startswith("planted:") for role in roles)
