from fjordpress.corpus import by_id
from fjordpress.fixtures import hops_for
from fjordpress.hops import extractive_from_windows, run_hops
from fjordpress.packing import PackedWindow


def test_alignment_mismatch_raises():
    try:
        run_hops("x", ["kun en"], ["one", "two"], "g", "g")
    except ValueError as exc:
        assert "differ" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_oracle_backtranslate_recovers_gold_danish_sentences():
    art = by_id()["vk-001"]
    rec = hops_for(art, pack_budget=40)
    # Every oracle-back sentence should be one of the source sentences.
    from fjordpress.sentences import split_sentences

    src = set(art.danish_sentences)
    for sent in split_sentences(rec.danish_back_oracle):
        assert sent in src


def test_oracle_english_is_the_gold_parallel():
    art = by_id()["vk-005"]
    rec = hops_for(art)
    assert rec.english_oracle == art.english


def test_gloss_hop_is_not_identical_to_oracle():
    art = by_id()["vk-002"]
    rec = hops_for(art)
    assert rec.english_gloss != rec.english_oracle
    assert rec.danish_back_gloss != rec.danish_back_oracle


def test_windows_are_non_empty():
    art = by_id()["vk-006"]
    rec = hops_for(art, pack_budget=30)
    assert rec.windows
    assert all(w.n_sentences >= 1 for w in rec.windows)


def test_extractive_from_windows_lead():
    windows = [
        PackedWindow(["A one.", "A two."], 4),
        PackedWindow(["B one."], 2),
    ]
    assert extractive_from_windows(windows, per_window=1) == "A one. B one."
    assert extractive_from_windows(windows, per_window=0) == ""
