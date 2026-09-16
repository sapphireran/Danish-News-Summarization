from fjordpress.corpus import (
    TEST_IDS,
    TRAIN_IDS,
    VALIDATION_IDS,
    all_articles,
    articles_for,
    split_map,
    validate_corpus,
)
from fjordpress.entities import mention_in_text


def test_corpus_validates_and_covers_splits():
    assert validate_corpus() == []
    assert len(all_articles()) == 10
    ids = {art.article_id for art in all_articles()}
    assigned = set(TRAIN_IDS) | set(VALIDATION_IDS) | set(TEST_IDS)
    assert ids == assigned
    assert len(TRAIN_IDS) == 6
    assert len(VALIDATION_IDS) == 2
    assert len(TEST_IDS) == 2


def test_every_entity_appears_in_the_danish_source():
    missing = []
    for art in all_articles():
        for ent in art.entities:
            if not mention_in_text(ent, art.danish):
                missing.append((art.article_id, ent))
    assert missing == []


def test_gold_summaries_are_shorter_than_sources():
    for art in all_articles():
        assert len(art.gold_da_summary) < len(art.danish)
        assert len(art.gold_en_summary) < len(art.english)


def test_articles_for_and_split_map():
    train = articles_for(TRAIN_IDS)
    assert [a.article_id for a in train] == list(TRAIN_IDS)
    assert set(split_map()) == {"train", "validation", "test"}
    try:
        articles_for(["nope"])
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError")


def test_sections_are_known():
    allowed = {"harbour", "energy", "school", "culture", "transport"}
    assert {art.section for art in all_articles()} <= allowed
