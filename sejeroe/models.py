"""Dataclasses for the Sejerø Tidende closed world."""

from __future__ import annotations

from dataclasses import dataclass, field


SLOT_NAMES = ("who", "what", "when", "where", "why", "how")


@dataclass(frozen=True)
class SlotCard:
    """Gold 5W1H card written before any hop, not inferred from a CSV."""

    who: str
    what: str
    when: str
    where: str
    why: str
    how: str
    aliases: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def surface_forms(self, name: str) -> tuple[str, ...]:
        canonical = getattr(self, name)
        extras = self.aliases.get(name, ())
        seen: list[str] = []
        for item in (canonical, *extras):
            if item and item not in seen:
                seen.append(item)
        return tuple(seen)


@dataclass(frozen=True)
class Quote:
    speaker: str
    danish: str
    english: str
    cue_da: str
    cue_en: str


@dataclass(frozen=True)
class PlantedError:
    """A deliberately broken Danish summary used to show metric blind spots."""

    kind: str
    summary_da: str
    dropped_slots: tuple[str, ...] = ()
    note: str = ""


@dataclass(frozen=True)
class Article:
    id: str
    headline_da: str
    body_da: str
    body_en: str
    summary_en: str
    summary_da: str
    oracle_da: str
    slots: SlotCard
    quotes: tuple[Quote, ...]
    connectives_da: tuple[str, ...]
    planted: tuple[PlantedError, ...]
    split: str  # train / validation / test

    @property
    def lead_da(self) -> str:
        from sejeroe.sentences import first_sentence

        return first_sentence(self.body_da)

    @property
    def lead_en(self) -> str:
        from sejeroe.sentences import first_sentence

        return first_sentence(self.body_en)
