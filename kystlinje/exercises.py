"""Auto-gradable workbook questions derived from the live ledger."""

from __future__ import annotations

from dataclasses import dataclass

from .corpus import all_briefs, brief_by_id
from .ledger import (
    build_all_ledgers,
    hop_loss_table,
    mean_survival,
    worst_end_to_end,
)
from .pack import pack_article


@dataclass(frozen=True)
class Question:
    number: int
    prompt: str
    answer: str
    kind: str  # exact | contains


def questions() -> list[Question]:
    ledgers = build_all_ledgers()
    loss = hop_loss_table(ledgers)
    worst_pair = max(loss, key=lambda item: (item[2], item[0], item[1]))
    worst_hop = f"{worst_pair[0]}->{worst_pair[1]}"
    worst_brief = worst_end_to_end(ledgers)
    year_ids = [
        brief.id
        for brief in all_briefs()
        for err in brief.planted
        if err.code == "YEAR-SHIFT"
    ]
    time_ids = [
        brief.id
        for brief in all_briefs()
        for err in brief.planted
        if err.code == "TIME-SHIFT"
    ]
    name_ids = [
        brief.id
        for brief in all_briefs()
        for err in brief.planted
        if err.code == "NAME-STUCK"
    ]
    long_id = max(all_briefs(), key=lambda b: len(b.body_da)).id
    long_brief = brief_by_id(long_id)
    packs = pack_article(long_brief.body_da, budget=80, unit="char")
    silver_mean = mean_survival(ledgers, "silver")
    lead_mean = mean_survival(ledgers, "lead2")
    better_control = "lead2" if lead_mean >= silver_mean else "silver"

    return [
        Question(
            1,
            "Which directed hop loses the most source entities on average? "
            "Answer as start->end using source, pivot, summary, silver.",
            worst_hop,
            "exact",
        ),
        Question(
            2,
            "Which brief id has the lowest end-to-end (source→silver) entity survival?",
            worst_brief.brief.id,
            "exact",
        ),
        Question(
            3,
            "Which brief plants a YEAR-SHIFT (1904 becoming 1914)?",
            year_ids[0] if year_ids else "",
            "exact",
        ),
        Question(
            4,
            "Which brief plants a TIME-SHIFT on the night ferry?",
            time_ids[0] if time_ids else "",
            "exact",
        ),
        Question(
            5,
            "Which brief flattens Lærke into Larke and never restores æ?",
            name_ids[0] if name_ids else "",
            "exact",
        ),
        Question(
            6,
            "How many Kystlinje briefs are in the handwritten corpus?",
            str(len(all_briefs())),
            "exact",
        ),
        Question(
            7,
            f"At character budget 80, how many packed windows does {long_id} produce?",
            str(len(packs)),
            "exact",
        ),
        Question(
            8,
            "On this fiction set, which keeps more source entities on average: "
            "lead2 or silver?",
            better_control,
            "exact",
        ),
        Question(
            9,
            "What column name does translate.py read for the Danish article body?",
            "article text",
            "exact",
        ),
        Question(
            10,
            "finetune.py saves ./large_model. Which local directory does eval.py load?",
            "small_model",
            "contains",
        ),
    ]


def grade(number: int, attempt: str) -> tuple[bool, str]:
    q = next(item for item in questions() if item.number == number)
    got = _norm(attempt)
    expected = _norm(q.answer)
    if q.kind == "contains":
        ok = expected in got or got in expected
    else:
        ok = got == expected
    return ok, q.answer


def _norm(text: str) -> str:
    return " ".join((text or "").strip().casefold().split())
