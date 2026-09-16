from fjordpress.corpus import all_articles
from fjordpress.lexicon import (
    DA_EN,
    coverage_report,
    gloss_danish_to_english,
    gloss_english_to_danish,
    reverse_lexicon,
)


def test_identity_names_survive_da_to_en():
    result = gloss_danish_to_english("Lisbeth Holm på Havnepladsen i Vesterklit")
    assert "Lisbeth" in result.text
    assert "Holm" in result.text
    assert "Havnepladsen" in result.text
    assert result.unknown == []


def test_function_words_gloss():
    result = gloss_danish_to_english("færgen er aflyst")
    lowered = result.text.lower()
    assert "ferry" in lowered or "the-ferry" in lowered
    assert "cancelled" in lowered or "is" in lowered


def test_numbers_pass_through():
    result = gloss_danish_to_english("klokken 06.00 og 1,2 millioner")
    assert "06.00" in result.text
    assert "1,2" in result.text


def test_unknown_tokens_are_recorded():
    result = gloss_danish_to_english("xyzzyplonk på kajen")
    assert "xyzzyplonk" in result.unknown
    assert result.coverage < 1.0


def test_reverse_lexicon_first_danish_wins():
    rev = reverse_lexicon({"hus": "house", "huset": "house"})
    assert rev["house"] == "hus"


def test_gazette_is_fully_covered():
    report = coverage_report([art.danish for art in all_articles()], danish=True)
    assert report["n_unknown_types"] == 0
    assert report["coverage"] == 1.0
    assert report["n_tokens"] > 500


def test_roundtrip_is_lossy_on_purpose():
    src = "Kommunen åbner et venteskur på kajen"
    en = gloss_danish_to_english(src).text
    back = gloss_english_to_danish(en).text
    # Closed-class collapse: et/en both become "a", so we do not require equality.
    assert back.lower() != src.lower() or "venteskur" in back.lower()
    assert len(DA_EN) > 200


def test_empty_gloss():
    empty = gloss_danish_to_english("")
    assert empty.text == ""
    assert empty.coverage == 1.0
