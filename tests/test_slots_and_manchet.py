from sejeroe.fixtures import article_by_id
from sejeroe.manchet import score_manchet
from sejeroe.quotes import score_article_quotes
from sejeroe.slots import score_slots


def test_body_keeps_every_canonical_slot_surface() -> None:
    article = article_by_id("SEJ-001")
    score = score_slots(article.slots, article.body_da, article.id, "body_da")
    # HOW aliases include SMS / extra sailing, which are in the body.
    assert score.recall == 1.0
    assert score.missing == ()


def test_silver_ferry_lede_covers_four_manchet_slots() -> None:
    article = article_by_id("SEJ-001")
    manchet = score_manchet(article, article.summary_da, "summary_da")
    assert manchet.coverage == 1.0
    assert manchet.misses == ()
    assert "eftermiddag" in manchet.lead


def test_silver_drops_how_and_the_quote() -> None:
    article = article_by_id("SEJ-001")
    slots = score_slots(article.slots, article.summary_da, article.id, "summary_da")
    assert "how" in slots.missing
    quotes = score_article_quotes(article, article.summary_da, "summary_da")
    assert quotes[0].span_hit is False
    assert quotes[0].kept is False


def test_oracle_keeps_the_spoken_extra_sailing() -> None:
    article = article_by_id("SEJ-001")
    quotes = score_article_quotes(article, article.oracle_da, "oracle_da")
    assert quotes[0].kept is True
    assert quotes[0].speaker_hit is True


def test_who_swap_loses_havnsoe_in_first_sentence() -> None:
    article = article_by_id("SEJ-001")
    planted = article.planted[0]
    assert planted.kind == "who-swap"
    manchet = score_manchet(article, planted.summary_da, "planted")
    assert "where" in manchet.misses or "who" in manchet.misses
