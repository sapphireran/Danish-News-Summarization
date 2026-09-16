from sejeroe.figures import score_figures
from sejeroe.fixtures import article_by_id
from sejeroe.stylebook import grade, grade_roles


def test_body_keeps_all_gold_figures() -> None:
    article = article_by_id("SEJ-001")
    score = score_figures(article, article.body_da, "body_da")
    assert score.recall == 1.0
    assert score.missing == ()


def test_silver_ferry_drops_some_figures() -> None:
    article = article_by_id("SEJ-001")
    score = score_figures(article, article.summary_da, "summary_da")
    assert score.total == 3
    # Silver keeps 18.30; 40 passengers and 15 m/s usually fall out of the T5 hop.
    assert "18.30" not in score.missing
    assert score.recall < 1.0


def test_silver_fails_quote_gate_on_ferry() -> None:
    article = article_by_id("SEJ-001")
    silver = grade(article, article.summary_da, "silver_da")
    lead1 = grade(article, article.lead_da, "lead1_da")
    assert "quote_or_speaker" in silver.failed
    assert silver.passed < silver.total
    assert "who_in_lede" in {gate.name for gate in lead1.gates if gate.passed}


def test_grade_roles_covers_three_texts() -> None:
    article = article_by_id("SEJ-005")
    roles = grade_roles(article)
    assert set(roles) == {"lead1_da", "silver_da", "oracle_da"}
    planted = article.planted[0]
    book = grade(article, planted.summary_da, "planted")
    assert "what_in_lede" in book.failed or "figures_majority" in book.failed or not book.ok
