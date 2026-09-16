"""Extract and compare Danish measures: numbers, units, clocks, dates, money.

Silver-label hops (DA→EN→T5→DA) quietly rewrite the *surface* of a number
even when the story survives. This module turns those surfaces into
comparable records so a ledger can say ``2,4 ha`` became ``24 ha``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Iterable

MONTHS = {
    "januar": 1,
    "februar": 2,
    "marts": 3,
    "april": 4,
    "maj": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}

EN_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

# Longer unit strings first so ``t/ha`` wins over ``t`` and ``mg/l`` over ``l``.
_UNIT_ALIASES = {
    "mm": "mm",
    "cm": "cm",
    "km": "km",
    "m": "m",
    "ha": "ha",
    "kg": "kg",
    "t": "t",
    "ton": "t",
    "liter": "l",
    "l": "l",
    "mw": "MW",
    "min": "min",
    "min.": "min",
    "mg/l": "mg/l",
    "mg/L": "mg/l",
    "t/ha": "t/ha",
    "kg/ha": "kg/ha",
    "m/s": "m/s",
    "kr": "kr",
    "kr.": "kr",
    "dkk": "kr",
    "dollar": "dollar",
    "dollars": "dollar",
    "%": "%",
    "pct": "%",
    "pct.": "%",
    "elever": "count:elever",
    "brandfolk": "count:brandfolk",
}

_KINDS = {
    "mm": "precip",
    "cm": "length",
    "km": "length",
    "m": "length",
    "ha": "area",
    "kg": "mass",
    "t": "mass",
    "l": "volume",
    "MW": "power",
    "min": "duration",
    "mg/l": "conc",
    "t/ha": "yield",
    "kg/ha": "yield",
    "m/s": "speed",
    "kr": "money",
    "dollar": "money",
    "%": "percent",
}


@dataclass(frozen=True)
class Measure:
    kind: str
    raw: str
    value: Decimal | None
    unit: str
    start: int
    end: int
    sign: int = 1
    scale: str = ""  # mio / mia
    extra: str = ""  # month, feast, line id, clock partner
    notes: tuple[str, ...] = field(default_factory=tuple)

    def normalized(self) -> tuple[str, Decimal | None, str]:
        value = self.value
        if value is not None:
            value = value * self.sign
            if self.scale == "mio":
                value *= Decimal("1000000")
            elif self.scale == "mia":
                value *= Decimal("1000000000")
        return self.kind, value, self.unit


def parse_da_number(text: str) -> Decimal:
    """Parse a Danish or English numeric surface into ``Decimal``.

    * ``3.200`` (groups of three) → 3200
    * ``47,2`` → 47.2
    * ``1.234,56`` → 1234.56
    * ``47.2`` → 47.2
    """
    raw = text.strip().replace(" ", "")
    if not raw:
        raise ValueError("empty number")
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+,\d+", raw):
        raw = raw.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", raw):
        raw = raw.replace(".", "")
    elif re.fullmatch(r"\d{1,3}(?:,\d{3})+", raw):
        raw = raw.replace(",", "")
    elif re.fullmatch(r"\d{1,3}(?:,\d{3})+\.\d+", raw):
        raw = raw.replace(",", "")
    elif "," in raw and "." not in raw:
        raw = raw.replace(",", ".")
    try:
        return Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"not a number: {text!r}") from exc


def extract_measures(text: str) -> list[Measure]:
    """Return measures in left-to-right order without overlapping spans."""
    if not text:
        return []
    candidates: list[Measure] = []
    for finder in (
        _find_dimensions,
        _find_rates,
        _find_money,
        _find_temperature,
        _find_clocks,
        _find_clock_ranges,
        _find_dates,
        _find_percent,
        _find_feasts,
        _find_lines,
        _find_plain_units,
        _find_counts,
    ):
        candidates.extend(finder(text))
    return _resolve_overlaps(candidates)


def _resolve_overlaps(candidates: Iterable[Measure]) -> list[Measure]:
    ordered = sorted(
        candidates,
        key=lambda m: (m.start, -(m.end - m.start), -len(m.raw)),
    )
    kept: list[Measure] = []
    occupied: list[tuple[int, int]] = []
    for item in ordered:
        if any(not (item.end <= a or item.start >= b) for a, b in occupied):
            continue
        kept.append(item)
        occupied.append((item.start, item.end))
    kept.sort(key=lambda m: m.start)
    return kept


def _find_dimensions(text: str) -> list[Measure]:
    out: list[Measure] = []
    pattern = re.compile(
        r"(?P<a>\d+(?:[.,]\d+)?)\s*[×xX]\s*(?P<b>\d+(?:[.,]\d+)?)\s*(?P<u>m|cm|mm|km)\b"
    )
    for match in pattern.finditer(text):
        out.append(
            Measure(
                kind="dimension",
                raw=match.group(0),
                value=parse_da_number(match.group("a")),
                unit=f"{match.group('u')}x{match.group('u')}",
                start=match.start(),
                end=match.end(),
                extra=str(parse_da_number(match.group("b"))),
                notes=("width",),
            )
        )
    return out


def _find_rates(text: str) -> list[Measure]:
    out: list[Measure] = []
    pattern = re.compile(
        r"(?P<v>\d+(?:[.,]\d+)?)\s*(?P<u>t/ha|kg/ha|mg/l|mg/L|m/s)\b"
    )
    for match in pattern.finditer(text):
        unit = _UNIT_ALIASES[match.group("u")]
        out.append(
            Measure(
                kind=_KINDS[unit],
                raw=match.group(0),
                value=parse_da_number(match.group("v")),
                unit=unit,
                start=match.start(),
                end=match.end(),
            )
        )
    return out


def _find_money(text: str) -> list[Measure]:
    out: list[Measure] = []
    scaled = re.compile(
        r"(?P<v>\d+(?:[.,]\d+)?)\s*(?P<scale>mio|mia|million)\.?\s*(?P<cur>kr\.?|DKK|dollar|dollars)?",
        flags=re.IGNORECASE,
    )
    for match in scaled.finditer(text):
        currency = (match.group("cur") or "kr").lower()
        unit = "dollar" if "dollar" in currency else "kr"
        out.append(
            Measure(
                kind="money",
                raw=match.group(0).strip(),
                value=parse_da_number(match.group("v")),
                unit=unit,
                start=match.start(),
                end=match.end(),
                scale="mio" if match.group("scale").lower() in {"mio", "million"} else match.group("scale").lower(),
            )
        )
    thousands = re.compile(
        r"(?P<v>\d{1,3}(?:\.\d{3})+)\s*(?P<cur>kr\.?|DKK)\b",
        flags=re.IGNORECASE,
    )
    for match in thousands.finditer(text):
        out.append(
            Measure(
                kind="money",
                raw=match.group(0),
                value=parse_da_number(match.group("v")),
                unit="kr",
                start=match.start(),
                end=match.end(),
                notes=("thousands",),
            )
        )
    dollars = re.compile(
        r"(?P<v>\d{1,3}(?:\.\d{3})+|\d+(?:[.,]\d+)?)\s+(?P<cur>dollar|dollars)\b",
        flags=re.IGNORECASE,
    )
    for match in dollars.finditer(text):
        out.append(
            Measure(
                kind="money",
                raw=match.group(0),
                value=parse_da_number(match.group("v")),
                unit="dollar",
                start=match.start(),
                end=match.end(),
            )
        )
    simple = re.compile(
        r"(?P<v>\d+(?:[.,]\d+)?)\s*(?P<cur>kr\.?)\b",
        flags=re.IGNORECASE,
    )
    for match in simple.finditer(text):
        out.append(
            Measure(
                kind="money",
                raw=match.group(0),
                value=parse_da_number(match.group("v")),
                unit="kr",
                start=match.start(),
                end=match.end(),
            )
        )
    return out


def _find_temperature(text: str) -> list[Measure]:
    out: list[Measure] = []
    pattern = re.compile(
        r"(?P<sign>[−–-])?(?P<v>\d+(?:[.,]\d+)?)\s*(?:°\s*)?C\b"
    )
    for match in pattern.finditer(text):
        sign = -1 if match.group("sign") else 1
        raw = match.group(0)
        out.append(
            Measure(
                kind="temperature",
                raw=raw,
                value=parse_da_number(match.group("v")),
                unit="C",
                start=match.start(),
                end=match.end(),
                sign=sign,
            )
        )
    return out


def _find_clocks(text: str) -> list[Measure]:
    out: list[Measure] = []
    pattern = re.compile(
        r"(?:kl\.\s*)?(?P<h>\d{1,2})[.:](?P<m>\d{2})(?!\s*[–-])",
        flags=re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        hour = int(match.group("h"))
        minute = int(match.group("m"))
        if hour > 23 or minute > 59:
            continue
        # ``3.200 kr.`` is a thousand-grouped amount, not 03:20.
        if match.end() < len(text) and text[match.end()].isdigit():
            continue
        out.append(
            Measure(
                kind="clock",
                raw=match.group(0).strip(),
                value=Decimal(hour * 60 + minute),
                unit="min_of_day",
                start=match.start(),
                end=match.end(),
                extra=f"{hour:02d}:{minute:02d}",
            )
        )
    return out


def _find_clock_ranges(text: str) -> list[Measure]:
    out: list[Measure] = []
    pattern = re.compile(
        r"(?P<h1>\d{1,2})[.:](?P<m1>\d{2})\s*[–-]\s*(?P<h2>\d{1,2})[.:](?P<m2>\d{2})"
    )
    for match in pattern.finditer(text):
        out.append(
            Measure(
                kind="clock_range",
                raw=match.group(0),
                value=Decimal(int(match.group("h1")) * 60 + int(match.group("m1"))),
                unit="min_of_day",
                start=match.start(),
                end=match.end(),
                extra=f"{int(match.group('h2')):02d}:{int(match.group('m2')):02d}",
            )
        )
    return out


def _find_dates(text: str) -> list[Measure]:
    out: list[Measure] = []
    months = "|".join(MONTHS)
    pattern = re.compile(
        rf"\b(?P<d>\d{{1,2}})\.\s+(?P<m>{months})(?:\s+(?P<y>\d{{4}}))?\b",
        flags=re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        month = MONTHS[match.group("m").lower()]
        year = int(match.group("y") or 0)
        day = int(match.group("d"))
        value = Decimal(year * 10000 + month * 100 + day) if year else Decimal(month * 100 + day)
        out.append(
            Measure(
                kind="date",
                raw=match.group(0),
                value=value,
                unit="date",
                start=match.start(),
                end=match.end(),
                extra=match.group("m").lower(),
            )
        )
    en_months = "|".join(EN_MONTHS)
    en_pattern = re.compile(
        rf"\b(?P<d>\d{{1,2}})\s+(?P<m>{en_months})(?:\s+(?P<y>\d{{4}}))?\b",
        flags=re.IGNORECASE,
    )
    for match in en_pattern.finditer(text):
        month = EN_MONTHS[match.group("m").lower()]
        year = int(match.group("y") or 0)
        day = int(match.group("d"))
        value = Decimal(year * 10000 + month * 100 + day) if year else Decimal(month * 100 + day)
        out.append(
            Measure(
                kind="date",
                raw=match.group(0),
                value=value,
                unit="date",
                start=match.start(),
                end=match.end(),
                extra=match.group("m").lower(),
            )
        )
    return out


def _find_percent(text: str) -> list[Measure]:
    out: list[Measure] = []
    pattern = re.compile(r"(?P<v>\d+(?:[.,]\d+)?)\s*%")
    for match in pattern.finditer(text):
        out.append(
            Measure(
                kind="percent",
                raw=match.group(0),
                value=parse_da_number(match.group("v")),
                unit="%",
                start=match.start(),
                end=match.end(),
            )
        )
    return out


def _find_feasts(text: str) -> list[Measure]:
    out: list[Measure] = []
    pattern = re.compile(
        r"\b(?P<n>\d+)\.\s+søndag i (?P<feast>advent|fasten)\b",
        flags=re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        out.append(
            Measure(
                kind="feast",
                raw=match.group(0),
                value=Decimal(match.group("n")),
                unit="ordinal",
                start=match.start(),
                end=match.end(),
                extra=match.group("feast").lower(),
            )
        )
    pattern_cls = re.compile(r"\b(?P<n>\d+)\.\s+klasse\b", flags=re.IGNORECASE)
    for match in pattern_cls.finditer(text):
        out.append(
            Measure(
                kind="grade",
                raw=match.group(0),
                value=Decimal(match.group("n")),
                unit="ordinal",
                start=match.start(),
                end=match.end(),
                extra="klasse",
            )
        )
    pattern_year = re.compile(r"\byear\s+(?P<n>\d+)\b", flags=re.IGNORECASE)
    for match in pattern_year.finditer(text):
        out.append(
            Measure(
                kind="grade",
                raw=match.group(0),
                value=Decimal(match.group("n")),
                unit="ordinal",
                start=match.start(),
                end=match.end(),
                extra="klasse",
            )
        )
    words = {
        "first": 1,
        "1st": 1,
        "second": 2,
        "2nd": 2,
        "third": 3,
        "3rd": 3,
        "fourth": 4,
        "4th": 4,
    }
    en_feast = re.compile(
        r"\b(?:the\s+)?(?P<n>first|second|third|fourth|1st|2nd|3rd|4th|\d+)\s+"
        r"Sunday of (?P<feast>Advent|Lent)\b",
        flags=re.IGNORECASE,
    )
    for match in en_feast.finditer(text):
        raw_n = match.group("n").lower()
        number = words.get(raw_n, int(raw_n) if raw_n.isdigit() else 0)
        feast = "advent" if match.group("feast").lower() == "advent" else "fasten"
        out.append(
            Measure(
                kind="feast",
                raw=match.group(0),
                value=Decimal(number),
                unit="ordinal",
                start=match.start(),
                end=match.end(),
                extra=feast,
            )
        )
    return out


def _find_lines(text: str) -> list[Measure]:
    out: list[Measure] = []
    pattern = re.compile(r"\b(?:linje|line)\s+(?P<n>\d+)\b", flags=re.IGNORECASE)
    for match in pattern.finditer(text):
        out.append(
            Measure(
                kind="line",
                raw=match.group(0),
                value=Decimal(match.group("n")),
                unit="line",
                start=match.start(),
                end=match.end(),
            )
        )
    return out


def _find_plain_units(text: str) -> list[Measure]:
    out: list[Measure] = []
    pattern = re.compile(
        r"(?P<v>\d+(?:[.,]\d+)?)\s*(?P<u>mm|cm|km|ha|kg|MW|min\.?|liter)\b"
    )
    for match in pattern.finditer(text):
        unit_raw = match.group("u")
        unit = _UNIT_ALIASES.get(unit_raw, _UNIT_ALIASES.get(unit_raw.rstrip("."), unit_raw))
        kind = _KINDS.get(unit, "quantity")
        out.append(
            Measure(
                kind=kind,
                raw=match.group(0),
                value=parse_da_number(match.group("v")),
                unit=unit,
                start=match.start(),
                end=match.end(),
            )
        )
    # Bare metres that are not part of a dimension (24 × 44 m already claimed).
    metres = re.compile(r"(?P<v>\d+(?:[.,]\d+)?)\s*m\b")
    for match in metres.finditer(text):
        out.append(
            Measure(
                kind="length",
                raw=match.group(0),
                value=parse_da_number(match.group("v")),
                unit="m",
                start=match.start(),
                end=match.end(),
            )
        )
    tons = re.compile(r"(?P<v>\d+(?:[.,]\d+)?)\s*t\b")
    for match in tons.finditer(text):
        out.append(
            Measure(
                kind="mass",
                raw=match.group(0),
                value=parse_da_number(match.group("v")),
                unit="t",
                start=match.start(),
                end=match.end(),
            )
        )
    return out


def _find_counts(text: str) -> list[Measure]:
    out: list[Measure] = []
    pattern = re.compile(
        r"(?P<v>\d+)\s+(?P<u>elever|brandfolk|pupils|firefighters)\b",
        flags=re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        noun = match.group("u").lower()
        out.append(
            Measure(
                kind="count",
                raw=match.group(0),
                value=Decimal(match.group("v")),
                unit="count",
                start=match.start(),
                end=match.end(),
                extra=noun,
            )
        )
    return out
