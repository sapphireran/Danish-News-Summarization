from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlantedError:
    code: str
    source_raw: str
    silver_raw: str
    hop: str  # pivot | summary | silver
    note: str


@dataclass(frozen=True)
class Article:
    id: str
    title: str
    topic: str
    body_da: str
    pivot_en: str
    summary_en: str
    silver_da: str
    oracle_da: str
    planted: tuple[PlantedError, ...]
    lead2_da: str
