from fjordpress.metrics import compression_ratio, mean_rouge, ngrams, rouge_scores, token_jaccard


def test_identical_strings_are_one():
    s = rouge_scores("Færgen er aflyst i nat", "Færgen er aflyst i nat")
    assert s.rouge1 == 1.0
    assert s.rouge2 == 1.0
    assert s.rougeL == 1.0


def test_disjoint_strings_are_zero():
    s = rouge_scores("kaffe på kajen", "vindmøller på klitten")
    assert s.rouge1 == 0.0
    assert s.rouge2 == 0.0


def test_partial_overlap_between_zero_and_one():
    s = rouge_scores("færgen til Mågeø er aflyst", "færgen til Mågeø kører")
    assert 0.0 < s.rouge1 < 1.0
    assert s.rougeL > 0.0


def test_empty_pair_is_perfect_and_one_sided_is_zero():
    assert rouge_scores("", "").rouge1 == 1.0
    assert rouge_scores("hej", "").rouge1 == 0.0
    assert rouge_scores("", "hej").rouge1 == 0.0


def test_ngrams_and_jaccard():
    assert ngrams(["a", "b", "c"], 2) == [("a", "b"), ("b", "c")]
    assert ngrams(["a"], 2) == []
    assert token_jaccard("en to tre", "tre to en") == 1.0
    assert token_jaccard("en", "to") == 0.0


def test_compression_and_mean():
    assert compression_ratio("en to tre fire", "en to") == 0.5
    assert compression_ratio("", "en") == 0.0
    means = mean_rouge([("en to", "en to"), ("en", "to")])
    assert means["rouge1"] == 0.5
