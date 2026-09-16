from sejeroe.sentences import first_sentence, split_sentences
from sejeroe.fixtures import article_by_id


def test_abbreviation_and_clock_stay_in_one_sentence() -> None:
    text = (
        "Næste afgang ventes først kl. 18.30, hvis vinden lægger sig. "
        "Rederiet sender SMS."
    )
    sentences = split_sentences(text)
    assert len(sentences) == 2
    assert sentences[0].startswith("Næste afgang")
    assert "18.30" in sentences[0]


def test_danish_opening_quote_starts_a_sentence() -> None:
    text = (
        "Havnefogeden advarede tidligt. "
        "»Vi sætter en ekstra afgang ind i aften,« siger Møller. "
        "Rederiet følger op."
    )
    sentences = split_sentences(text)
    assert len(sentences) == 3
    assert sentences[1].startswith("»Vi sætter")


def test_decimal_and_english_abbrev() -> None:
    text = "Sales fell 22.5 percent, e.g. in November. The shop still opens."
    sentences = split_sentences(text)
    assert len(sentences) == 2
    assert "22.5" in sentences[0]


def test_ferry_brief_has_five_sentences() -> None:
    article = article_by_id("SEJ-001")
    sentences = split_sentences(article.body_da)
    assert len(sentences) == 5
    assert first_sentence(article.body_da).startswith("Sejerøfærgen")


def test_empty_and_whitespace() -> None:
    assert split_sentences("") == []
    assert split_sentences("   ") == []
    assert first_sentence("") == ""
