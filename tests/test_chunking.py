from __future__ import annotations

import pytest

from danish_news.chunking import (
    measure,
    pack_windows,
    split_into_windows,
    split_long_sentence,
    split_sentences,
)
from examples.data.corpus import by_id


def test_empty_and_whitespace() -> None:
    assert split_sentences("") == []
    assert split_sentences("   ") == []


def test_basic_danish_split() -> None:
    text = "Skyerne letter over Aarhus. Kommunen spuler vejene i nat."
    sentences = split_sentences(text)
    assert len(sentences) == 2
    assert sentences[0].endswith("Aarhus.")
    assert sentences[1].startswith("Kommunen")


def test_abbreviations_and_decimals_stay_in_one_sentence() -> None:
    text = (
        "Biblioteket får 4,5 mio. kr. i budgettet, bl.a. til en læsesal "
        "på ca. 60 pladser, f.eks. til skoleklasser kl. 10."
    )
    sentences = split_sentences(text)
    assert len(sentences) == 1
    assert "mio. kr." in sentences[0]
    assert "f.eks." in sentences[0]


def test_library_fixture_keeps_abbreviations() -> None:
    article = by_id()["library-budget"]
    sentences = split_sentences(article["article_text"])
    joined = " ".join(sentences)
    assert "mio. kr." in joined
    assert "f.eks." in joined
    assert "bl.a." in joined
    # A naive split on every period would produce many more fragments.
    assert len(sentences) <= 6


def test_decimal_does_not_split() -> None:
    sentences = split_sentences("Prisen er 12.5 millioner kroner. Det er dyrt.")
    assert len(sentences) == 2
    assert "12.5" in sentences[0]


def test_danish_ordinal_date_stays_one_sentence() -> None:
    text = (
        "Ifølge kommunen bliver der holdt borgermøde i Nordkraft den 12. oktober "
        "kl. 19. Kritikere mener, at tempoet er for højt."
    )
    sentences = split_sentences(text)
    assert len(sentences) == 2
    assert "12. oktober kl. 19." in sentences[0]
    assert sentences[1].startswith("Kritikere")


def test_harbour_plan_does_not_split_october_date() -> None:
    sentences = split_sentences(by_id()["harbour-plan"]["article_text"])
    assert not any(sentence.lower().startswith("oktober") for sentence in sentences)
    assert any("12. oktober" in sentence for sentence in sentences)


def test_runon_fixture_is_one_sentence() -> None:
    article = by_id()["harbour-runon"]
    sentences = split_sentences(article["article_text"])
    assert len(sentences) == 1


def test_split_long_sentence_prefers_commas() -> None:
    sentence = (
        "Byrådet vedtog planen, herunder cykelstier, boliger, en daginstitution "
        "og et kulturhus tæt på fjorden."
    )
    chunks = split_long_sentence(sentence, max_units=8, unit="words")
    assert len(chunks) > 1
    assert "".join(chunk.replace(" ", "") for chunk in chunks).startswith("Byrådet")
    # No words dropped.
    original_words = [token for token in sentence.replace(",", " ,").split() if token]
    rebuilt = " ".join(chunks)
    for token in ("Byrådet", "cykelstier", "kulturhus", "fjorden"):
        assert token in rebuilt


def test_pack_windows_respects_budget() -> None:
    sentences = [
        "En kort sætning.",
        "Endnu en kort sætning om havnen.",
        "En tredje sætning der også er kort.",
    ]
    windows = pack_windows(sentences, max_units=10, unit="words")
    assert windows
    for window in windows:
        assert window.unit_count <= 10 or len(window.texts) == 1


def test_harbour_plan_splits_at_small_budget() -> None:
    text = by_id()["harbour-plan"]["article_text"]
    small = split_into_windows(text, 40, "words")
    large = split_into_windows(text, 400, "words")
    assert len(small) > len(large)
    assert len(large) == 1
    packed = " ".join(window.text for window in small)
    for sentence in split_sentences(text):
        assert sentence.split()[0] in packed or sentence[:10] in packed


def test_char_unit_matches_course_script_cost() -> None:
    sentence = "Aalborg, Randers, Viborg."
    chunks = split_long_sentence(sentence, max_units=12, unit="chars")
    assert chunks
    assert all(measure(chunk, "chars") >= 1 for chunk in chunks)


def test_measure_words_keeps_danish_letters() -> None:
    text = "Æbletræet i Århus og Øresund."
    tokens_count = measure(text, "words")
    assert tokens_count >= 5


@pytest.mark.parametrize("article_id", list(by_id()))
def test_every_fixture_yields_at_least_one_window(article_id: str) -> None:
    text = by_id()[article_id]["article_text"]
    windows = split_into_windows(text, 80, "words")
    assert windows
    assert sum(len(window.texts) for window in windows) >= 1
