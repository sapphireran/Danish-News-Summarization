"""Hop-error catalog: invented teacher mistakes on the fictional briefs.

These items are teaching fixtures. They show the kinds of damage a
Danish→English→summarize→Danish hop can do. They are not measurements from
the 2023 GPU run — that printout was never committed.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

from .fiction import REPO_ROOT

DEFAULT_JSON = REPO_ROOT / "examples" / "data" / "error_items.json"

# Stable typology used in docs/error-catalog.md
ERROR_CODES = {
    "HOP-TR": "Forward translation bent a Danish fact or name.",
    "HOP-SM": "The English teacher invented or dropped content.",
    "HOP-BK": "Back-translation drifted away from the English summary.",
    "ENT": "Person, place, or organization was swapped.",
    "NUM": "A number, date, or time changed.",
    "TNS": "Tense or mood no longer matches the article.",
    "OMIS": "A load-bearing fact disappeared.",
    "ADD": "A fact that is not in the article appeared.",
    "STYLE": "English calque or leftover source-language word.",
}


@dataclass(frozen=True)
class ErrorItem:
    id: str
    article_id: str
    source_span: str
    silver_span: str
    codes: tuple[str, ...]
    severity: int
    explanation: str

    def code_labels(self) -> list[str]:
        return [f"{code}: {ERROR_CODES[code]}" for code in self.codes]


_ITEMS: tuple[ErrorItem, ...] = (
    ErrorItem(
        id="err-01",
        article_id="lab-01",
        source_span="Bestyrelsen forventer omkring 80 gæster",
        silver_span="Bestyrelsen venter omkring 18 gæster",
        codes=("HOP-TR", "NUM"),
        severity=4,
        explanation="80 became eighteen after a da→en hop that folded 'omkring 80' poorly.",
    ),
    ErrorItem(
        id="err-02",
        article_id="lab-01",
        source_span="Saturn kan ses i det største spejlteleskop",
        silver_span="Lørdag kan ses i det største spejlteleskop",
        codes=("HOP-TR", "ENT"),
        severity=5,
        explanation="Saturn/Saturday confusion is a classic English-pivot bruise.",
    ),
    ErrorItem(
        id="err-03",
        article_id="lab-01",
        source_span="Hvis skydækket bliver for tæt, flyttes kigget til søndag kl. 21",
        silver_span="Observatoriet åbner lørdag aften for offentligheden.",
        codes=("HOP-SM", "OMIS"),
        severity=3,
        explanation="The English teacher kept the lead and dropped the rain backup.",
    ),
    ErrorItem(
        id="err-04",
        article_id="lab-04",
        source_span="start i Skørping",
        silver_span="start i Skærbæk",
        codes=("HOP-BK", "ENT"),
        severity=4,
        explanation="Back-translation swapped two Jutland toponyms that share a Sk- onset.",
    ),
    ErrorItem(
        id="err-05",
        article_id="lab-06",
        source_span="udbyttet nok lander under 40 kilo",
        silver_span="udbyttet lander omkring 140 kilo",
        codes=("HOP-TR", "NUM"),
        severity=5,
        explanation="A dropped 'under' plus a spurious 1-prefix is a typical hop numeral error.",
    ),
    ErrorItem(
        id="err-06",
        article_id="lab-07",
        source_span="Favoritten er Inge Ravn fra Odense",
        silver_span="Favoritten er Inge Ravn fra Odessa",
        codes=("HOP-BK", "ENT"),
        severity=4,
        explanation="Odense/Odessa is the kind of named-entity drift mT5 will happily memorize.",
    ),
    ErrorItem(
        id="err-07",
        article_id="lab-08",
        source_span="flytter sig op til to meter på et vinterhalvår",
        silver_span="flytter sig op til to kilometer på et vinterhalvår",
        codes=("HOP-SM", "NUM"),
        severity=5,
        explanation="The English summarizer promoted a unit. Silver labels then teach the wrong scale.",
    ),
    ErrorItem(
        id="err-08",
        article_id="lab-09",
        source_span="Fire afgangsfilm fra den lille filmskole i Aarhus",
        silver_span="Five graduation films from the small film school in Aarhus get premiere.",
        codes=("HOP-SM", "NUM", "STYLE"),
        severity=4,
        explanation="The teacher counted wrong and the back-translation left English in the label.",
    ),
    ErrorItem(
        id="err-09",
        article_id="lab-11",
        source_span="Holstebro Ungdomskor letter onsdag mod Tórshavn",
        silver_span="Holstebro Ungdomskor letter onsdag mod Tromsø",
        codes=("HOP-TR", "ENT"),
        severity=4,
        explanation="Two North-Atlantic capitals swapped after the English hop.",
    ),
    ErrorItem(
        id="err-10",
        article_id="lab-12",
        source_span="Holstebros nye klatrehal åbner lørdag",
        silver_span="Holstebros nye klatrehal åbnede lørdag",
        codes=("TNS", "HOP-BK"),
        severity=2,
        explanation="Past tense leaked in from an English summary that already treated the opening as done.",
    ),
    ErrorItem(
        id="err-11",
        article_id="lab-15",
        source_span="målet i år er at slå 70",
        silver_span="målet i år er at slå 70, og NASA hjælper med artslisten",
        codes=("HOP-SM", "ADD"),
        severity=5,
        explanation="The English news T5 sometimes injects a global institution. That is not in the article.",
    ),
    ErrorItem(
        id="err-12",
        article_id="lab-16",
        source_span="sender hele dagen fra et telt på torvet i Thisted",
        silver_span="sender hele dagen from a tent on the square i Thisted",
        codes=("HOP-BK", "STYLE"),
        severity=3,
        explanation="A mixed Danish/English calque survived decoding. Fluency dies before faithfulness does.",
    ),
    ErrorItem(
        id="err-13",
        article_id="lab-02",
        source_span="overskuddet går til byens ungdomsskole",
        silver_span="overskuddet går til byens ungdomsskole og et nyt hotel",
        codes=("ADD", "HOP-SM"),
        severity=3,
        explanation="An extra beneficiary is a mild but teachable hallucination.",
    ),
    ErrorItem(
        id="err-14",
        article_id="lab-03",
        source_span="Headlineren er saxofonisten Naja Storm",
        silver_span="Headlineren er trompetisten Naja Storm",
        codes=("ENT", "HOP-TR"),
        severity=3,
        explanation="Instrument swap after 'saxophonist' was paraphrased and then mistranslated back.",
    ),
)


def all_items() -> tuple[ErrorItem, ...]:
    return _ITEMS


def load_catalog(path: Path | None = None) -> list[ErrorItem]:
    source = path or DEFAULT_JSON
    if source.is_file():
        raw = json.loads(source.read_text(encoding="utf-8"))
        return [
            ErrorItem(
                id=row["id"],
                article_id=row["article_id"],
                source_span=row["source_span"],
                silver_span=row["silver_span"],
                codes=tuple(row["codes"]),
                severity=int(row["severity"]),
                explanation=row["explanation"],
            )
            for row in raw
        ]
    return list(_ITEMS)


def dump_catalog_json(path: Path | None = None) -> Path:
    target = path or DEFAULT_JSON
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = []
    for item in _ITEMS:
        row = asdict(item)
        row["codes"] = list(item.codes)
        payload.append(row)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def items_for_article(article_id: str, items: Sequence[ErrorItem] | None = None) -> list[ErrorItem]:
    pool = list(items) if items is not None else list(_ITEMS)
    return [item for item in pool if item.article_id == article_id]
