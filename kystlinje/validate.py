"""Self-checks for the handwritten corpus, planted scars, and CSV contracts."""

from __future__ import annotations

from dataclasses import dataclass

from .corpus import SPLIT_IDS, all_briefs
from .danish import split_sentences
from .entities import extract_entities
from .ledger import build_all_ledgers, build_ledger
from .schemas import COURSE_SCHEMAS


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def run_checks() -> list[Check]:
    checks: list[Check] = []
    briefs = all_briefs()
    ids = [b.id for b in briefs]
    checks.append(Check("unique-ids", len(ids) == len(set(ids)), f"{len(ids)} briefs"))
    checks.append(Check("eighteen-briefs", len(briefs) == 18, str(len(briefs))))

    split_ids = [item for values in SPLIT_IDS.values() for item in values]
    checks.append(Check("split-cover", set(split_ids) == set(ids), f"{len(split_ids)} split ids"))
    checks.append(
        Check(
            "split-sizes",
            [len(SPLIT_IDS["train"]), len(SPLIT_IDS["validation"]), len(SPLIT_IDS["test"])] == [12, 3, 3],
            "12/3/3",
        )
    )

    for brief in briefs:
        sents = split_sentences(brief.body_da)
        checks.append(
            Check(
                f"{brief.id}-sentences",
                len(sents) >= 4,
                f"{len(sents)} sentences",
            )
        )
        checks.append(
            Check(
                f"{brief.id}-lead2",
                brief.lead2_da == " ".join(sents[:2]),
                brief.lead2_da[:48],
            )
        )
        source_ents = extract_entities(brief.body_da, article_id=brief.id)
        checks.append(
            Check(
                f"{brief.id}-has-entities",
                len(source_ents) >= 4,
                f"{len(source_ents)} entities",
            )
        )
        for err in brief.planted:
            haystack = {
                "pivot": brief.pivot_en,
                "summary": brief.summary_en,
                "silver": brief.silver_da,
            }[err.hop]
            source_ok = (not err.source_span) or (err.source_span in brief.body_da)
            # NAME-STUCK plants the flattened form on the pivot (and later hops).
            if err.code == "NAME-STUCK" and err.hop == "pivot":
                source_ok = "Lærke Holm" in brief.body_da
            drifted_ok = (not err.drifted_span) or (
                err.drifted_span.casefold() in haystack.casefold()
            )
            if err.code.startswith("DROP"):
                drifted_ok = True
                # The dropped span should be absent from the hop text when it
                # is a distinctive string (not a generic empty drift).
                if err.source_span and len(err.source_span) >= 3:
                    drifted_ok = err.source_span not in haystack
            checks.append(
                Check(
                    f"{brief.id}-{err.code}-source",
                    source_ok,
                    err.source_span,
                )
            )
            checks.append(
                Check(
                    f"{brief.id}-{err.code}-drift",
                    drifted_ok,
                    f"{err.hop}:{err.drifted_span}",
                )
            )

    # Specific planted numeric scars the workbook advertises.
    kz05 = next(b for b in briefs if b.id == "kz-05")
    checks.append(Check("kz-05-11-in-source", "11" in kz05.body_da, "11"))
    checks.append(Check("kz-05-12-in-silver", "12" in kz05.silver_da, kz05.silver_da))
    kz08 = next(b for b in briefs if b.id == "kz-08")
    checks.append(Check("kz-08-1904", "1904" in kz08.body_da and "1914" in kz08.silver_da, "year"))
    kz17 = next(b for b in briefs if b.id == "kz-17")
    checks.append(Check("kz-17-time", "23:40" in kz17.body_da and "23:30" in kz17.silver_da, "time"))
    kz07 = next(b for b in briefs if b.id == "kz-07")
    checks.append(Check("kz-07-larke", "Lærke Holm" in kz07.body_da and "Larke Holm" in kz07.silver_da, "name"))

    ledgers = build_all_ledgers()
    checks.append(Check("ledgers-built", len(ledgers) == 18, str(len(ledgers))))
    for led in ledgers:
        checks.append(
            Check(
                f"{led.brief.id}-source-rate-1",
                led.survival_rate("source") == 1.0,
                str(led.survival_rate("source")),
            )
        )

    # DROP-NUM on kz-01: 47 must be lost by summary.
    kz01 = build_ledger(next(b for b in briefs if b.id == "kz-01"))
    forty_seven = [row for row in kz01.rows if row.entity.value == "47"]
    checks.append(Check("kz-01-47-extracted", bool(forty_seven), "47"))
    if forty_seven:
        checks.append(
            Check(
                "kz-01-47-lost-in-summary",
                forty_seven[0].survived("pivot") and not forty_seven[0].survived("summary"),
                str(forty_seven[0].present),
            )
        )

    checks.append(Check("six-course-schemas", len(COURSE_SCHEMAS) == 6, str(len(COURSE_SCHEMAS))))
    source_schema = next(s for s in COURSE_SCHEMAS if s.name == "source-articles")
    checks.append(
        Check(
            "article-text-column",
            "article text" in source_schema.columns,
            ",".join(source_schema.columns),
        )
    )
    return checks


def summary(checks: list[Check] | None = None) -> tuple[int, int]:
    checks = checks if checks is not None else run_checks()
    ok = sum(1 for c in checks if c.ok)
    return ok, len(checks)
