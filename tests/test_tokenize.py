from fjordpress.tokenize import count_words, join_tokens, lowercase_words, tokenize_words


def test_keeps_danish_letters_and_accented_e():
    assert tokenize_words("én færge til Mågeø") == ["én", "færge", "til", "Mågeø"]


def test_keeps_decimals_times_and_thousands():
    tokens = tokenize_words("kl. 06.00 kostede 1,2 millioner og 12.000 sider")
    assert "06.00" in tokens
    assert "1,2" in tokens
    assert "12.000" in tokens


def test_peels_punctuation_and_join_reproduces_2023_scar():
    tokens = tokenize_words("Havnen, sagde hun.")
    assert tokens == ["Havnen", ",", "sagde", "hun", "."]
    assert join_tokens(tokens) == "Havnen , sagde hun ."


def test_hyphenated_names_stay_one_token():
    assert "El-Khatib" in tokenize_words("Yasmin El-Khatib skrev teksterne")


def test_lowercase_words_drops_bare_punct():
    assert lowercase_words("Fire, fem.") == ["fire", "fem"]


def test_count_words_ignores_commas():
    assert count_words("en, to, tre") == 3
    assert count_words("") == 0
    assert count_words("   ") == 0
