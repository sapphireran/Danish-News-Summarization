"""Closed gazetteer for Toftevig fixtures: names, amounts, dates, places."""

from __future__ import annotations

import re

PLACES = (
    "Toftevig",
    "Toftevig Havn",
    "Toftevig Kommune",
    "Gråfjord",
    "Gråfjord Dige",
    "Nørreholt Skole",
    "Østermarken",
    "Klintbro",
    "Færgelejet Klintbro",
    "Svanedammen",
    "Møllebakken",
    "Fiskerihallen",
    "Pakhuset",
    "Kirkevej",
    "Strandgade",
)

PEOPLE = (
    "Ellen Kragh",
    "Søren Vibe",
    "Mette Holm",
    "Kaj Overgaard",
    "Amina Rashid",
    "Niels Bro",
    "Lars Kjær",
    "Ida Frost",
)

ORGS = (
    "havneudvalget",
    "digelaget",
    "skolebestyrelsen",
    "teknik- og miljøudvalget",
    "biblioteket",
    "færgeselskabet",
)

# Surface forms that a silver label should try to keep.
FIGURE_PATTERNS = (
    re.compile(r"\b\d{1,2}\.\s*(?:oktober|november|december|januar|marts|april|maj|juni|juli|august|september)\b", re.I),
    re.compile(r"\bkl\.\s*\d{1,2}\.\d{2}\b", re.I),
    re.compile(r"\b\d+(?:[.,]\d+)?\s*mio\.\s*kr\.", re.I),
    re.compile(r"\b\d+(?:[.,]\d+)?\s*pct\.", re.I),
    re.compile(r"\bnr\.\s*\d+\b", re.I),
    re.compile(r"\b\d+(?:[.,]\d+)?\s*km\b", re.I),
    re.compile(r"\b\d{4}\b"),
    re.compile(r"\b\d+(?:[.,]\d+)?\s*kr\.", re.I),
    re.compile(r"\bDKK\s*\d+(?:[.,]\d+)?(?:\s*million)?\b", re.I),
    re.compile(r"\b\d{1,2}\.\d{2}\s*a\.m\.", re.I),
    re.compile(r"\b\d{1,2}\.\d{2}\s*p\.m\.", re.I),
    re.compile(r"\bno\.\s*\d+\b", re.I),
    re.compile(
        r"\b\d{1,2}\s+(?:January|March|April|June|July|August|September|October|November|December)\b",
        re.I,
    ),
    re.compile(r"\b\d+(?:[.,]\d+)?\s*percent\b", re.I),
)

NAME_RE = re.compile(
    r"\b(?:Toftevig Havn|Toftevig Kommune|Færgelejet Klintbro|Nørreholt Skole|"
    r"Gråfjord Dige|Gråfjord|Toftevig|Østermarken|Klintbro|Svanedammen|"
    r"Møllebakken|Fiskerihallen|Pakhuset|Kirkevej|Strandgade|"
    r"Ellen Kragh|Søren Vibe|Mette Holm|Kaj Overgaard|Amina Rashid|"
    r"Niels Bro|Lars Kjær|Ida Frost)\b"
)


def find_figures(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for pattern in FIGURE_PATTERNS:
        for match in pattern.finditer(text):
            surface = re.sub(r"\s+", " ", match.group(0)).strip()
            key = surface.lower()
            if key not in seen:
                seen.add(key)
                found.append(surface)
    return found


def find_names(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for match in NAME_RE.finditer(text):
        surface = match.group(0)
        if surface not in seen:
            seen.add(surface)
            found.append(surface)
    return found


def contains_figure(text: str) -> bool:
    return bool(find_figures(text))
