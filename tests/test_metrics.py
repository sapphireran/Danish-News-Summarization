from danish_news_sum.metrics import (
    aggregate_scores,
    compression_ratio,
    lcs_f1,
    lexical_scores,
    ngram_f1,
    tokenize,
)


def test_tokenize_lowercases_and_drops_punctuation():
    assert tokenize("Hej, Aarhus!") == ["hej", "aarhus"]


def test_identical_strings_score_perfect_overlap():
    text = "Metroen åbner i Sydhavn i oktober."
    scores = ngram_f1(text, text, n=1)
    assert scores == {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    assert lcs_f1(text, text)["f1"] == 1.0


def test_unrelated_strings_score_zero_unigram_overlap():
    scores = ngram_f1("katte sover", "cykler kører", n=1)
    assert scores["f1"] == 0.0


def test_partial_overlap_is_between_zero_and_one():
    scores = ngram_f1(
        "Kommunen planter tusind nye træer i Odense",
        "Odense kommune planter nye træer",
        n=1,
    )
    assert 0.0 < scores["f1"] < 1.0


def test_bigram_is_stricter_than_unigram():
    prediction = "ny metro i københavn åbner snart"
    reference = "københavn åbner en ny metro snart"
    unigram = ngram_f1(prediction, reference, n=1)["f1"]
    bigram = ngram_f1(prediction, reference, n=2)["f1"]
    assert unigram > bigram


def test_compression_ratio_is_article_over_summary():
    article = "ord " * 20
    summary = "ord " * 5
    assert compression_ratio(article, summary) == 4.0


def test_lexical_scores_include_compression_when_article_given():
    scores = lexical_scores(
        prediction="Odense planter træer.",
        reference="Odense planter mange træer.",
        article="Odense kommune planter ti tusind træer langs de nye cykelstier.",
    )
    assert scores["compression_ratio"] > 1.0
    assert "rouge1_f1" in scores
    assert "rougeL_f1" in scores


def test_aggregate_scores_averages_rows():
    rows = [
        {"rouge1_f1": 1.0, "rouge2_f1": 0.5},
        {"rouge1_f1": 0.5, "rouge2_f1": 0.25},
    ]
    assert aggregate_scores(rows) == {"rouge1_f1": 0.75, "rouge2_f1": 0.375}
