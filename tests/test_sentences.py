"""Sentence splitters: clocks, ordinal dates, and naive over-cuts."""

from __future__ import annotations

from pakhus.corpus import get_article
from pakhus.sentences import count_false_boundaries, split_danish, split_naive


def test_clock_stays_in_one_sentence() -> None:
    text = "Mødet begynder den 12. oktober kl. 19.30 i Pakhuset."
    sents = split_danish(text)
    assert len(sents) == 1
    assert "kl. 19.30" in sents[0]


def test_naive_cuts_ordinal_date() -> None:
    text = "Digelaget mødtes torsdag den 3. oktober kl. 18.30 i Pakhuset."
    naive = split_naive(text)
    danish = split_danish(text)
    assert naive[0].endswith("den 3.")
    assert len(danish) == 1
    assert "kl. 18.30" in danish[0]


def test_mio_kr_not_a_boundary() -> None:
    text = "Anlægget koster 18,4 mio. kr. og graves i marts."
    sents = split_danish(text)
    assert len(sents) == 1
    assert "18,4 mio. kr." in sents[0]


def test_bl_a_protected() -> None:
    text = "Der afsættes midler bl.a. til kaj, dige og pakhus. Sagen fortsætter."
    sents = split_danish(text)
    assert len(sents) == 2
    assert sents[0].startswith("Der afsættes")
    assert sents[1].startswith("Sagen")


def test_nr_and_att() -> None:
    text = "Indgangen er Strandgade nr. 14, att. havneudvalget."
    sents = split_danish(text)
    assert len(sents) == 1


def test_tof003_naive_cuts_more() -> None:
    article = get_article("tof-003")
    counts = count_false_boundaries(article.danish)
    assert counts["extra_naive_cuts"] >= 8
    assert counts["danish_sentences"] == article.n_sentences


def test_empty_and_whitespace() -> None:
    assert split_danish("") == []
    assert split_naive("   ") == []


def test_question_and_next_uppercase() -> None:
    text = "Kommer bussen? Ellen Kragh svarer i morgen."
    assert len(split_danish(text)) == 2
