from sejeroe.align import align_article
from sejeroe.baseline import baselines_for, comparison_table, extractive_lede
from sejeroe.fixtures import ARTICLES, article_by_id
from sejeroe.sentences import split_sentences


def test_extractive_lead_is_first_sentence() -> None:
    article = article_by_id("SEJ-001")
    lead = extractive_lede(article.body_da, 1)
    assert lead == split_sentences(article.body_da)[0]
    two = extractive_lede(article.body_da, 2)
    assert lead in two
    assert two.startswith(lead)


def test_lead1_beats_or_matches_silver_on_ferry_manchet() -> None:
    article = article_by_id("SEJ-001")
    table = comparison_table(article)
    assert table["lead1_manchet"] >= table["silver_manchet"]
    names = [row.name for row in baselines_for(article)]
    assert names == ["lead1_da", "lead2_da", "silver_da", "oracle_da"]


def test_every_brief_is_sentence_aligned() -> None:
    for article in ARTICLES:
        alignment = align_article(article)
        assert alignment.aligned, article.id
        assert len(alignment.pairs) == 5
        assert alignment.quote_index is not None
        quote = alignment.pairs[alignment.quote_index]
        assert quote.is_quote
        assert quote.danish.startswith("»")
