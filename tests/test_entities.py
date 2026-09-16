from fjordpress.entities import (
    extract_entities,
    extract_numbers,
    fold,
    mention_in_text,
    missing_mentions,
    retention_ratio,
    retention_table,
    unique_preserve,
)


def test_fold_hyphen_and_case():
    assert fold("El-Khatib") == fold("el khatib")


def test_mention_matches_substring_and_tokens():
    text = "Yasmin El-Khatib skrev teksterne på Amberhus"
    assert mention_in_text("Yasmin El-Khatib", text)
    assert mention_in_text("Amberhus", text)
    assert not mention_in_text("Klitsand", text)


def test_numbers_and_retention():
    text = "Reparationen koster 1,2 millioner kroner kl. 06.00"
    assert "1,2" in extract_numbers(text)
    assert "06.00" in extract_numbers(text)
    gold = ["1,2", "Amberhus"]
    assert retention_ratio(text, gold) == 0.5
    assert missing_mentions(text, gold) == ["Amberhus"]


def test_retention_table_and_unique():
    hops = [("src", "Lisbeth Holm på Havnepladsen"), ("sum", "Havnepladsen")]
    table = retention_table(hops, ["Lisbeth Holm", "Havnepladsen"])
    assert table[0]["retention"] == 1.0
    assert table[1]["lost"] == ["Lisbeth Holm"]
    assert unique_preserve(["A", "a", "B"]) == ["A", "B"]


def test_empty_gold_is_full_retention():
    hits = extract_entities("hej", [])
    assert hits == []
    assert retention_ratio("hej", []) == 1.0
