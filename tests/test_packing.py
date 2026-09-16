from fjordpress.packing import (
    ApproxSubwordCounter,
    CharPlusOneCounter,
    WordTokenCounter,
    pack_article,
    pack_like_translate_back,
    pack_pieces,
    packing_stats,
    split_long_sentence,
)


def test_split_long_sentence_cuts_on_comma_under_budget():
    sentence = "alpha, bravo, charlie"
    chunks = split_long_sentence(sentence, max_length=12)
    # Character+1 budget is small, so comma cuts should fire.
    assert len(chunks) >= 2
    assert any("," in chunk for chunk in chunks[:-1])


def test_split_long_sentence_overflows_last_word():
    sentence = "abcdefghij klmnopqrst"
    chunks = split_long_sentence(sentence, max_length=12)
    assert len(chunks) == 2
    assert chunks[1].startswith("klmnopqrst") or "klmnopqrst" in chunks[1]


def test_pack_pieces_starts_new_window_on_overflow():
    windows = pack_pieces(
        ["aaaa", "bbbb", "cccc"],
        text_max_length=2,
        counter=WordTokenCounter(),
    )
    assert [w.n_sentences for w in windows] == [1, 1, 1]


def test_pack_article_multiple_windows_on_gazette_budget():
    text = (
        "Første sætning er kort. Anden sætning er også kort. "
        "Tredje sætning lukker rækken. Fjerde sætning kommer med."
    )
    windows = pack_article(text, text_max_length=8)
    assert len(windows) >= 2
    assert sum(w.n_sentences for w in windows) == 4


def test_translate_back_does_not_char_split():
    # A long comma-heavy sentence stays one piece when oversized split is off.
    long = "ord, " * 40 + "slut."
    back = pack_like_translate_back(long, max_length=500)
    faithful = pack_article(long, text_max_length=40)
    assert len(faithful) >= 1
    # translate_back-style packing uses 500 and no long-sentence split,
    # so the whole thing is typically one window.
    assert len(back) == 1


def test_counters_disagree_on_purpose():
    text = "Direktør Lisbeth Holm sagde"
    words = WordTokenCounter().count(text)
    chars = CharPlusOneCounter().count(text)
    approx = ApproxSubwordCounter(1.3).count(text)
    assert words == 4
    assert chars > words
    assert approx >= words


def test_packing_stats_empty():
    stats = packing_stats([])
    assert stats["n_windows"] == 0
    assert stats["mean_budget"] == 0.0


def test_rejects_non_positive_budget():
    try:
        split_long_sentence("hej", 0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
