"""Cascade, concatenation cap, and Toftevig fixture invariants."""

from __future__ import annotations

from pakhus.concat import rouge_l, score_concat, truncate_to_units
from pakhus.corpus import ARTICLES, get_article
from pakhus.hops import run_article, run_corpus
from pakhus.tokenize import approx_encode_len
from pakhus.world import find_figures, find_names


def test_ten_articles_unique_ids() -> None:
    ids = [a.id for a in ARTICLES]
    assert len(ids) == 10
    assert len(set(ids)) == 10
    assert {a.split for a in ARTICLES} == {"train", "validation", "test"}


def test_parallel_sentence_counts() -> None:
    for article in ARTICLES:
        for da, en in article.pairs:
            assert da.strip() and en.strip()


def test_harbour_story_has_clock_money_and_names() -> None:
    article = get_article("tof-001")
    figures = find_figures(article.danish)
    names = find_names(article.danish)
    assert any("19.30" in f or "kl. 19.30" in f for f in figures)
    assert any("18,4" in f for f in figures)
    assert "Søren Vibe" in names
    assert "Toftevig Havn" in names


def test_cascade_repacks_tof001() -> None:
    row = run_article(get_article("tof-001"))
    assert row.hop1.n_panes == 2
    assert row.hop2.n_panes == 2
    # English naive split is finer than Danish news split, so hop 2
    # sentence counts should not match hop 1 crate contents 1:1.
    hop1_sents = sum(p.n_sentences for p in row.hop1.panes)
    hop2_sents = sum(p.n_sentences for p in row.hop2.panes)
    assert hop2_sents != hop1_sents
    assert row.concat.would_truncate_at_128
    assert "Toftevig Havn" in row.concat.echo_names
    assert row.concat.pane0_share < 0.7


def test_label_cap_chops_units() -> None:
    text = "ord " * 400
    kept = truncate_to_units(text, 128)
    assert approx_encode_len(kept) <= 128
    assert approx_encode_len(text) > 128


def test_oracle_rouge_nonzero() -> None:
    row = run_article(get_article("tof-009"))
    score = rouge_l(row.danish_silver, row.article.oracle_summary_da)
    assert score > 0.2


def test_run_corpus_ten_rows() -> None:
    cascade = run_corpus()
    assert cascade.article_ids() == [a.id for a in ARTICLES]
    scores = [r.concat for r in cascade.rows]
    assert any(s.would_truncate_at_128 for s in scores)


def test_score_concat_short_article() -> None:
    article = get_article("tof-009")
    score = score_concat(article.id, article.english)
    assert score.n_panes == 1
    assert score.would_truncate_at_128 is False
    assert score.figure_survival >= 0.5
