from sejeroe.fixtures import article_by_id
from sejeroe.hops import HOP_ORDER, hop_records, hop_text
from sejeroe.length import compound_hits, pair_lengths
from sejeroe.tokenize import LengthNotion


def test_hop_order_matches_course_scripts() -> None:
    article = article_by_id("SEJ-001")
    records = hop_records(article)
    assert tuple(item.hop for item in records) == HOP_ORDER
    assert hop_text(article, "raw_da") == article.body_da
    assert hop_text(article, "labeled_da") == article.summary_da
    assert "translate.py" in records[1].course_script
    assert "summary.py" in records[2].course_script
    assert "translate_back.py" in records[3].course_script


def test_english_body_is_not_shorter_in_words() -> None:
    article = article_by_id("SEJ-001")
    pair = pair_lengths(article, LengthNotion.WORDS)
    assert pair.english >= pair.danish
    assert pair.ratio >= 1.0


def test_ferry_compound_is_listed() -> None:
    article = article_by_id("SEJ-001")
    hits = compound_hits(article.body_da)
    assert "Sejerøfærgen" in hits or "færgeafgang" in hits or "SMS-varslingen" in hits
