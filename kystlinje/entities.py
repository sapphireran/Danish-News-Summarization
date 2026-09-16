"""Extract and match entities across Danish / English hops."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .danish import normalize
from .world import COMPOUNDS, GAZETTEER_BY_LENGTH, WorldEntry

_TIME = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")
_YEAR = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")
_NUMBER = re.compile(r"\b(\d+(?:[.,]\d+)?)\b")
_MONEY = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*(?:kr\.?|dkk|kroner)\b", re.IGNORECASE)
_KG = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*(?:kg|kilo)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Entity:
    key: str
    kind: str
    surface: str
    aliases: tuple[str, ...]
    value: str | None = None
    span: tuple[int, int] | None = None

    def match_needles(self) -> tuple[str, ...]:
        needles = list(self.aliases)
        if self.surface and self.surface not in needles:
            needles.append(self.surface)
        if self.value and self.value not in needles:
            needles.append(self.value)
        return tuple(needles)


@dataclass
class SpanMask:
    """Boolean mask so shorter gazetteer hits cannot overlap longer ones."""

    text: str
    taken: list[bool] = field(init=False)

    def __post_init__(self) -> None:
        self.taken = [False] * len(self.text)

    def free(self, start: int, end: int) -> bool:
        return not any(self.taken[start:end])

    def mark(self, start: int, end: int) -> None:
        for i in range(start, end):
            self.taken[i] = True


def extract_entities(text: str, *, article_id: str = "") -> list[Entity]:
    """Gazetteer + numbers + a short compound list, left-to-right."""
    if not text:
        return []
    found: list[Entity] = []
    mask = SpanMask(text)
    found.extend(_gazetteer_hits(text, mask))
    found.extend(_numeric_hits(text, mask, article_id))
    found.extend(_compound_hits(text, mask))
    return found


def _gazetteer_hits(text: str, mask: SpanMask) -> list[Entity]:
    hits: list[Entity] = []
    lowered = text.casefold()
    for entry in GAZETTEER_BY_LENGTH:
        for alias in sorted(entry.aliases, key=len, reverse=True):
            needle = alias.casefold()
            start = 0
            while True:
                index = lowered.find(needle, start)
                if index < 0:
                    break
                end = index + len(needle)
                if _bounded(text, index, end) and mask.free(index, end):
                    mask.mark(index, end)
                    hits.append(
                        Entity(
                            key=entry.key,
                            kind=entry.kind,
                            surface=text[index:end],
                            aliases=entry.aliases,
                            span=(index, end),
                        )
                    )
                start = index + 1
    return hits


def _bounded(text: str, start: int, end: int) -> bool:
    left_ok = start == 0 or not _is_word_char(text[start - 1])
    right_ok = end == len(text) or not _is_word_char(text[end])
    return left_ok and right_ok


def _is_word_char(ch: str) -> bool:
    return ch.isalnum() or ch in {"Æ", "Ø", "Å", "æ", "ø", "å"}


def _numeric_hits(text: str, mask: SpanMask, article_id: str) -> list[Entity]:
    hits: list[Entity] = []
    prefix = f"{article_id}:" if article_id else ""

    for rx, kind, key_prefix in (
        (_TIME, "time", "time"),
        (_MONEY, "money", "money"),
        (_KG, "measure", "kg"),
        (_YEAR, "year", "year"),
    ):
        for match in rx.finditer(text):
            if not mask.free(match.start(), match.end()):
                continue
            surface = match.group(0)
            value = _canonical_value(match, kind)
            mask.mark(match.start(), match.end())
            hits.append(
                Entity(
                    key=f"{prefix}{key_prefix}:{value}",
                    kind=kind,
                    surface=surface,
                    aliases=(surface, value),
                    value=value,
                    span=match.span(),
                )
            )

    for match in _NUMBER.finditer(text):
        if not mask.free(match.start(), match.end()):
            continue
        surface = match.group(1)
        # Skip lone digits that are house numbers inside already-taken spans.
        if len(surface) == 1 and int(surface) < 2:
            continue
        value = _number_value(surface)
        mask.mark(match.start(), match.end())
        hits.append(
            Entity(
                key=f"{prefix}num:{value}",
                kind="number",
                surface=surface,
                aliases=(surface, value),
                value=value,
                span=match.span(),
            )
        )
    return hits


def _canonical_value(match: re.Match[str], kind: str) -> str:
    if kind == "time":
        return f"{int(match.group(1)):02d}:{match.group(2)}"
    if kind == "year":
        return match.group(1)
    return _number_value(match.group(1))


def _number_value(surface: str) -> str:
    if re.fullmatch(r"\d{1,2}:\d{2}", surface):
        hh, mm = surface.split(":")
        return f"{int(hh):02d}:{mm}"
    if "," in surface and "." not in surface:
        return surface.replace(",", ".")
    if "." in surface and surface.count(".") == 1 and len(surface.split(".")[1]) == 3:
        # 1.234 Danish thousand — not used in this corpus, but keep honest.
        return surface.replace(".", "")
    return surface


def _compound_hits(text: str, mask: SpanMask) -> list[Entity]:
    hits: list[Entity] = []
    lowered = text.casefold()
    for compound in sorted(COMPOUNDS, key=len, reverse=True):
        start = 0
        while True:
            index = lowered.find(compound, start)
            if index < 0:
                break
            end = index + len(compound)
            if _bounded(text, index, end) and mask.free(index, end):
                mask.mark(index, end)
                hits.append(
                    Entity(
                        key=f"compound:{compound}",
                        kind="compound",
                        surface=text[index:end],
                        aliases=(compound,),
                        span=(index, end),
                    )
                )
            start = index + 1
    return hits


def entity_survives(entity: Entity, text: str) -> bool:
    """True if any alias or canonical value occurs in *text*."""
    if not text:
        return False
    folded = normalize(text)
    raw = text.casefold()
    for needle in entity.match_needles():
        n = normalize(needle)
        if not n:
            continue
        if _short_or_numeric(n):
            if _bounded_numeric(n, folded) or _bounded_numeric(n, raw):
                return True
            continue
        if n in folded or needle.casefold() in raw:
            return True
    if entity.value:
        value = entity.value
        if _bounded_numeric(value, text) or _bounded_numeric(value, folded):
            return True
        comma = value.replace(".", ",")
        if comma != value and _bounded_numeric(comma, text):
            return True
    return False


def _short_or_numeric(needle: str) -> bool:
    return needle.isdigit() or bool(re.fullmatch(r"\d+[.,:]\d+", needle)) or len(needle) <= 2


def _bounded_numeric(needle: str, text: str) -> bool:
    return re.search(rf"(?<!\d){re.escape(needle)}(?!\d)", text) is not None


def unique_by_key(entities: list[Entity]) -> list[Entity]:
    seen: dict[str, Entity] = {}
    for ent in entities:
        seen.setdefault(ent.key, ent)
    return list(seen.values())


def gazetteer_entry(key: str) -> WorldEntry | None:
    for entry in GAZETTEER_BY_LENGTH:
        if entry.key == key:
            return entry
    return None
