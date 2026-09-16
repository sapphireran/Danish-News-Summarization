from fjordpress.sentences import first_sentences, split_sentences


def test_split_plain_danish_news():
    text = (
        "Kommunen åbner et venteskur. Næste vurdering sker i morgen. "
        "Eleverne kører med bus."
    )
    assert split_sentences(text) == [
        "Kommunen åbner et venteskur.",
        "Næste vurdering sker i morgen.",
        "Eleverne kører med bus.",
    ]


def test_does_not_split_on_kl_and_time():
    text = "Næste vurdering sker kl. 06.00, når beredskabet har nye tal."
    assert split_sentences(text) == [text]


def test_does_not_split_f_eks_and_bl_a():
    text = "Der er problemer, f.eks. støj, bl.a. om natten, osv."
    sents = split_sentences(text)
    assert len(sents) == 1


def test_does_not_split_ordinal_date_before_month():
    text = "Høringen slutter den 3. maj, og rapporten lægges frem."
    assert len(split_sentences(text)) == 1


def test_splits_on_question_and_exclaim():
    text = "Kommer færgen? Nej! Kommunen venter."
    assert split_sentences(text) == ["Kommer færgen?", "Nej!", "Kommunen venter."]


def test_ellipsis_does_not_invent_empty_sentences():
    text = "Vinden vender... Kommunen venter."
    sents = split_sentences(text)
    assert len(sents) == 2
    assert sents[1] == "Kommunen venter."


def test_empty_and_none():
    assert split_sentences("") == []
    assert split_sentences("   ") == []
    assert split_sentences(None) == []


def test_lead_k():
    text = "En. To. Tre."
    assert first_sentences(text, 2) == "En. To."
    assert first_sentences(text, 0) == ""
    assert first_sentences(text, 9) == "En. To. Tre."
