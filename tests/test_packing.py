from sejeroe.fixtures import article_by_id
from sejeroe.packing import MANCHET_TIGHT, PRESETS, pack_report_rows, pack_text
from sejeroe.tokenize import LengthNotion, measure, words


def test_tight_budget_makes_several_windows() -> None:
    article = article_by_id("SEJ-001")
    windows = pack_text(article.body_da, MANCHET_TIGHT)
    assert len(windows) >= 3
    assert windows[0].token_count <= MANCHET_TIGHT.budget
    assert "Sejerøfærgen" in windows[0].text


def test_forward_hop_keeps_a_short_brief_in_one_window() -> None:
    article = article_by_id("SEJ-008")
    windows = pack_text(article.body_da, PRESETS["forward-hop"])
    assert len(windows) == 1
    assert windows[0].token_count == measure(article.body_da, LengthNotion.ROUGH_SUBWORD)


def test_pack_report_covers_named_presets() -> None:
    article = article_by_id("SEJ-003")
    rows = pack_report_rows(article.body_da)
    names = {row["policy"] for row in rows}
    assert names == set(PRESETS)
    for row in rows:
        assert row["windows"] >= 1
        assert row["budget"] > 0


def test_word_count_matches_tokenizer_helper() -> None:
    text = "Sejerøfærgen til Havnsø bliver aflyst."
    assert measure(text, LengthNotion.WORDS) == len(words(text))
    assert measure(text, LengthNotion.ROUGH_SUBWORD) >= measure(text, LengthNotion.WORDS)
