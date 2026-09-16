"""Column contracts for every CSV the course scripts read or write.

Keep this file aligned with docs/datasets.md and the hard-coded names in
the root ``*.py`` scripts. The example validator imports these tuples so a
renamed column fails in one place.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

# Stage names match files under examples/data/.
SCHEMAS: dict[str, tuple[str, ...]] = {
    "raw": ("id", "article text"),
    "translated": ("id", "body", "translated"),
    "summarized": ("id", "body", "translated", "summary"),
    "labeled": ("id", "body", "summary"),
    "finetune": ("id", "body", "summary"),
    "eval": ("input_text", "target_text", "text_len", "summary_len"),
}

# Language we expect a native reader to see in each text column.
COLUMN_LANGUAGE = {
    "article text": "da",
    "body": "da",
    "translated": "en",
    "summary_en": "en",
    "summary_da": "da",
    "input_text": "da",
    "target_text": "da",
}

DANISH_MARKERS = frozenset("æøåÆØÅ")


def required_columns(stage: str) -> tuple[str, ...]:
    try:
        return SCHEMAS[stage]
    except KeyError as exc:
        known = ", ".join(sorted(SCHEMAS))
        raise KeyError(f"unknown stage {stage!r}; expected one of: {known}") from exc


def missing_columns(stage: str, columns: Sequence[str]) -> list[str]:
    have = set(columns)
    return [name for name in required_columns(stage) if name not in have]


def extra_columns(stage: str, columns: Sequence[str]) -> list[str]:
    allowed = set(required_columns(stage))
    return [name for name in columns if name not in allowed]


def looks_danish(text: str) -> bool:
    """Cheap heuristic: Danish prose almost always uses æ/ø/å in a news article."""
    return any(ch in DANISH_MARKERS for ch in text)


def looks_english(text: str) -> bool:
    """Cheap heuristic: English sample rows should not be stuffed with æ/ø/å."""
    if not text.strip():
        return False
    marker_hits = sum(ch in DANISH_MARKERS for ch in text)
    return marker_hits <= 1


def row_is_complete(row: Mapping[str, object], stage: str) -> list[str]:
    blanks = []
    for name in required_columns(stage):
        value = row.get(name)
        if value is None or (isinstance(value, float) and value != value):
            blanks.append(name)
            continue
        if isinstance(value, str) and not value.strip():
            blanks.append(name)
    return blanks
