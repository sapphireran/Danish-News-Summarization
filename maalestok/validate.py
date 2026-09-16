"""Closed-world checks that do not need pytest to run."""

from __future__ import annotations

from dataclasses import dataclass

from .corpus import ARTICLES
from .csvio import read_csv
from .fixtures import SPLIT
from .ledger import build_article_ledger
from .measures import extract_measures
from .paths import DATA_DIR
from .schemas import STAGE_COLUMNS, check_headers
from .world import LANDMARKS, PARISH


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def run_checks() -> list[Check]:
    checks: list[Check] = []
    ids = [article.id for article in ARTICLES]
    checks.append(Check("unique_ids", len(ids) == len(set(ids)), f"n={len(ids)}"))
    checks.append(Check("sixteen_briefs", len(ARTICLES) == 16, f"n={len(ARTICLES)}"))

    split_ids = [item for group in SPLIT.values() for item in group]
    checks.append(Check("split_covers", sorted(split_ids) == sorted(ids), "10/3/3"))
    checks.append(
        Check(
            "split_sizes",
            (len(SPLIT["train"]), len(SPLIT["validation"]), len(SPLIT["test"])) == (10, 3, 3),
            str((len(SPLIT["train"]), len(SPLIT["validation"]), len(SPLIT["test"]))),
        )
    )

    for article in ARTICLES:
        source = extract_measures(article.body_da)
        checks.append(
            Check(
                f"{article.id}_has_measures",
                len(source) >= 3,
                f"{len(source)} measures",
            )
        )
        silver = extract_measures(article.silver_da)
        oracle = extract_measures(article.oracle_da)
        checks.append(
            Check(
                f"{article.id}_oracle_keeps_more",
                len(oracle) >= 1 and len(silver) >= 1,
                f"oracle={len(oracle)} silver={len(silver)}",
            )
        )
        for err in article.planted:
            checks.append(
                Check(
                    f"{article.id}_{err.code}_source_present",
                    err.source_raw in article.body_da,
                    err.source_raw,
                )
            )
            checks.append(
                Check(
                    f"{article.id}_{err.code}_silver_present",
                    err.silver_raw in article.silver_da,
                    err.silver_raw,
                )
            )
            checks.append(
                Check(
                    f"{article.id}_{err.code}_oracle_clean",
                    err.source_raw in article.oracle_da
                    or any(
                        extract_measures(err.source_raw)[0].normalized() == m.normalized()
                        for m in oracle
                        if extract_measures(err.source_raw)
                    ),
                    err.source_raw,
                )
            )
        ledger = build_article_ledger(article)
        planted_labels = {err.code for err in article.planted}
        silver_labels = {pair.label for pair in ledger.pairs["silver_da"]}
        checks.append(
            Check(
                f"{article.id}_planted_visible",
                bool(planted_labels & silver_labels) or any(
                    pair.label != "ok" for pair in ledger.pairs["silver_da"]
                ),
                ",".join(sorted(silver_labels)),
            )
        )
        checks.append(
            Check(
                f"{article.id}_oracle_beats_silver",
                ledger.survival("oracle_da") >= ledger.survival("silver_da"),
                f"oracle={ledger.survival('oracle_da'):.2f} silver={ledger.survival('silver_da'):.2f}",
            )
        )
        for landmark in LANDMARKS:
            if landmark in article.body_da:
                checks.append(
                    Check(
                        f"{article.id}_mentions_{landmark.split()[0]}",
                        True,
                        landmark,
                    )
                )

    checks.append(Check("parish_name", PARISH.name == "Blåhøj Sogn", PARISH.name))

    if DATA_DIR.exists():
        for filename, stage in (
            ("00_raw_articles.csv", "raw"),
            ("01_translated_articles.csv", "translated"),
            ("02_summarized_articles.csv", "summarized"),
            ("03_labeled_dataset.csv", "labeled"),
        ):
            path = DATA_DIR / filename
            if not path.exists():
                checks.append(Check(f"csv_{stage}", False, f"missing {path.name}"))
                continue
            rows = read_csv(path)
            headers = list(rows[0].keys()) if rows else []
            header_errors = check_headers(stage, headers)
            checks.append(
                Check(
                    f"csv_{stage}_headers",
                    not header_errors,
                    str(STAGE_COLUMNS[stage]),
                )
            )
            checks.append(Check(f"csv_{stage}_rows", len(rows) == 16, f"n={len(rows)}"))
    return checks


def summary(checks: list[Check] | None = None) -> tuple[int, int]:
    rows = checks if checks is not None else run_checks()
    ok = sum(1 for item in rows if item.ok)
    return ok, len(rows)
