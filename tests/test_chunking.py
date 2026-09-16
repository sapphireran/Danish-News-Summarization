from danish_news_sum.chunking import (
    describe_windows,
    pack_sentences,
    simple_sent_tokenize,
    split_article,
    split_into_sentences,
    split_long_sentence,
    whitespace_token_count,
)


def test_whitespace_token_count_treats_punctuation_separately():
    assert whitespace_token_count("Hej, verden!") == 4


def test_simple_sent_tokenize_splits_danish_and_english():
    text = (
        "København åbner en ny metrostation i efteråret. "
        "Borgmesteren kalder det et løft for Sydhavn. "
        "Dr. Hansen siger, at projektet er i tidsplan."
    )
    sentences = simple_sent_tokenize(text)
    assert len(sentences) >= 2
    assert sentences[0].startswith("København")


def test_split_long_sentence_breaks_on_commas_before_hard_limit():
    sentence = "alpha, " * 20 + "omega"
    chunks = split_long_sentence(sentence, max_length=40)
    assert len(chunks) > 1
    assert all(len(chunk) <= 50 for chunk in chunks)


def test_pack_sentences_starts_new_window_when_budget_exceeded():
    pairs = [("one", 4), ("two", 4), ("three", 4)]
    windows = pack_sentences(pairs, max_length=8)
    assert windows == [["one", "two"], ["three"]]


def test_split_into_sentences_splits_long_article_into_windows():
    article = " ".join(f"Sætning nummer {i} handler om lokalpolitik i Aarhus." for i in range(12))
    windows = split_into_sentences(article, text_max_length=20)
    assert len(windows) >= 2
    assert all(isinstance(window, list) and window for window in windows)


def test_split_article_joins_windows_and_covers_source_tokens():
    article = (
        "Fiskere på Vestkysten rapporterer færre torsk i år. "
        "Biologer peger på varmere vand og ændrede vandrestrømme. "
        "Kommunen lover en ny havneplan inden jul."
    )
    windows = split_article(article, text_max_length=16)
    assert windows
    joined = " ".join(windows)
    assert "torsk" in joined
    assert "havneplan" in joined


def test_describe_windows_returns_diagnostics():
    article = "Første sætning. Anden sætning. Tredje sætning om Odense."
    rows = describe_windows(article, text_max_length=8)
    assert rows
    assert {"window_index", "token_count", "char_count", "sentence_count", "preview"} <= set(rows[0])
    assert rows[0]["window_index"] == 0
