"""Course packers: character saw, empty-list scar, consistent baseline."""

from __future__ import annotations

from pakhus.corpus import get_article
from pakhus.packing import (
    ascii_atlas,
    character_vs_token_demo,
    pack_consistent,
    pack_course_back,
    pack_course_translate,
    split_long_sentence_course,
)
from pakhus.tokenize import approx_encode_len, char_word_len, word_tokenize


def test_tof001_spills_two_panes() -> None:
    article = get_article("tof-001")
    result = pack_course_translate(article.danish)
    assert result.n_panes == 2
    assert result.n_empty == 0
    assert result.panes[0].fill_ratio > 0.8
    assert result.panes[0].pane_id == 0
    assert result.panes[1].pane_id == 1


def test_tof009_single_underfilled_pane() -> None:
    article = get_article("tof-009")
    result = pack_course_translate(article.danish)
    assert result.n_panes == 1
    assert result.panes[0].fill_ratio < 0.4


def test_character_saw_overfragments_tof008() -> None:
    article = get_article("tof-008")
    long_da = article.pairs[0][0]
    demo = character_vs_token_demo(long_da, budget=460)
    assert demo["char_word_len"] > demo["approx_encode_len"]
    assert demo["course_saw_chunks"] >= 10
    course = pack_course_translate(article.danish)
    consistent = pack_consistent(article.danish)
    assert course.saw_fragments > consistent.saw_fragments
    assert course.n_panes >= 2
    assert "UNDERFILLED" in ascii_atlas(course, article.id)


def test_long_token_emits_empty_chunk() -> None:
    monster = "x" * 500
    chunks = split_long_sentence_course(monster, max_length=460)
    assert chunks[0] == ""
    assert monster in chunks[-1]


def test_back_translation_empty_list_scar() -> None:
    article = get_article("tof-010")
    assert approx_encode_len(article.english) > 512
    result = pack_course_back(article.english)
    assert result.n_empty == 1
    assert result.panes[0].empty
    assert result.panes[0].unit_sum == 0
    assert result.panes[1].over_budget
    consistent = pack_consistent(article.english, budget=512)
    assert consistent.n_empty == 0
    assert all(not p.empty for p in consistent.panes)


def test_course_join_spaces_punctuation() -> None:
    chunks = split_long_sentence_course(
        "Kajak, kajak, kajak, kajak og kajak, kajak.", max_length=20
    )
    assert any(" ," in chunk for chunk in chunks)


def test_char_len_counts_space() -> None:
    tokens = word_tokenize("Toftevig Havn")
    assert char_word_len(tokens) == sum(len(t) + 1 for t in tokens)
