"""Gazetteer for the fictional Hjelmøerne island chain.

Every name is original. These are not TV2 Nord / Nordjylland-News strings
and they are not copied from any employer corpus.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorldEntry:
    key: str
    kind: str  # person | place | org | work
    danish: str
    aliases: tuple[str, ...]


def _entry(kind: str, key: str, danish: str, *aliases: str) -> WorldEntry:
    unique = (danish, *aliases)
    return WorldEntry(key=key, kind=kind, danish=danish, aliases=unique)


PLACES: tuple[WorldEntry, ...] = (
    _entry("place", "place:hjelmoerne", "Hjelmøerne", "the Hjelm islands", "Hjelm islands"),
    _entry("place", "place:hjelmhoj", "Hjelmhøj", "Hjelmhoj"),
    _entry("place", "place:klinto", "Klintø", "Klinto"),
    _entry("place", "place:saltore", "Saltøre", "Saltore"),
    _entry("place", "place:mageodde", "Mågeodde", "Mageodde"),
    _entry("place", "place:ravnskar", "Ravnskær", "Ravnskaer", "Ravnskar"),
    _entry("place", "place:sognehavn", "Sognehavn"),
    _entry("place", "place:gradyb", "Grådyb", "Gradyb", "Graadyb"),
    _entry("place", "place:aeblehaven", "Æblehaven", "Aeblehaven", "Apple orchard", "the orchard"),
    _entry("place", "place:torveengen", "Tørveengen", "Torveengen"),
    _entry("place", "place:sandvig", "Sandvig"),
    _entry("place", "place:vesterklit", "Vesterklit"),
    _entry("place", "place:fogedtoften", "Fogedtoften"),
    _entry("place", "place:broagerstien", "Broagerstien"),
    _entry("place", "place:lynghuset", "Lynghuset"),
    _entry("place", "place:faergelejet", "Færgelejet", "Faergelejet", "the ferry berth"),
    _entry("place", "place:toldkammeret", "toldkammeret", "toldkammer", "customs house", "old customs house"),
)

PEOPLE: tuple[WorldEntry, ...] = (
    _entry("person", "person:signe-brix", "Signe Brix", "Brix"),
    _entry("person", "person:kaj-nygaard", "Kaj Nygaard", "Nygaard"),
    _entry("person", "person:petra-skov", "Petra Skov"),
    _entry("person", "person:laerke-holm", "Lærke Holm", "Laerke Holm", "Larke Holm"),
    _entry("person", "person:otto-kvist", "Otto Kvist"),
    _entry("person", "person:ida-fjaltring", "Ida Fjaltring"),
    _entry("person", "person:niels-orum", "Niels Ørum", "Niels Orum"),
    _entry("person", "person:bo-hjelm", "Bo Hjelm"),
    _entry("person", "person:mira-holst", "Mira Holst"),
    _entry("person", "person:ellen-krag", "Ellen Krag"),
    _entry("person", "person:troels-dam", "Troels Dam"),
    _entry("person", "person:astrid-mose", "Astrid Mose"),
    _entry("person", "person:viggo-tranberg", "Viggo Tranberg"),
    _entry("person", "person:katrine-bla", "Katrine Blå", "Katrine Bla", "Katrine Blaa"),
    _entry("person", "person:esben-kilde", "Esben Kilde"),
    _entry("person", "person:rune-holst", "Rune Holst"),
)

ORGS: tuple[WorldEntry, ...] = (
    _entry("org", "org:kystlinje", "Kystlinje", "Kystlinje magazine"),
    _entry("org", "org:skakklub", "Klintø Skakklub", "Klinto Chess Club", "Klintø Chess Club", "chess club"),
    _entry("org", "org:messing", "Hjelmhøj Messingorkester", "Hjelmhoj Brass Band", "Hjelmhøj Brass Band", "brass band"),
    _entry("org", "org:bageri", "Sognehavn Bageri", "Sognehavn Bakery"),
    _entry("org", "org:laesehus", "Sognehavn Læsehus", "Sognehavn Lasehus", "Sognehavn reading house"),
    _entry("org", "org:faerge", "Grådyb Færgeselskab", "Gradyb Ferry", "Graadyb Ferry Company"),
    _entry("org", "org:biavl", "Tørveengen Biavl", "Torveengen Beekeepers"),
    _entry("org", "org:glas", "Sandvig Glasværksted", "Sandvig Glasvaerksted", "Sandvig glass workshop"),
    _entry("org", "org:filmlaug", "Ravnskær Filmlaug", "Ravnskaer Film Guild"),
    _entry("org", "org:lastcykel", "Saltøre Lastcykel", "Saltore Cargo Bike", "cargo-bike cooperative"),
    _entry("org", "org:strikkelav", "Klintø Strikkelav", "Klinto Knitting Guild"),
    _entry("org", "org:teater", "Hjelmhøj Teaterlaug", "Hjelmhoj Theatre Guild"),
    _entry("org", "org:museum", "Vesterklit Vejrfløjemuseum", "Vesterklit Weather-Vane Museum"),
    _entry("org", "org:keramik", "Fogedtoften Keramik", "Fogedtoften Pottery"),
    _entry("org", "org:tang", "Mågeodde Tangkompagni", "Mageodde Seaweed Company"),
    _entry("org", "org:tryk", "Saltøre Tryk", "Saltore Press"),
)

WORKS: tuple[WorldEntry, ...] = (
    _entry("work", "work:toervestykket", "Tørvestykket", "Torvestykket", "The Peat Play"),
    _entry("work", "work:nattens-færge", "Nattens færge", "Night Ferry"),
)

GAZETTEER: tuple[WorldEntry, ...] = PLACES + PEOPLE + ORGS + WORKS

# Longest surface first so "Klintø Skakklub" wins over "Klintø".
GAZETTEER_BY_LENGTH: tuple[WorldEntry, ...] = tuple(
    sorted(GAZETTEER, key=lambda e: max(len(a) for a in e.aliases), reverse=True)
)

# Danish compounds we expect the pivot to either keep, split, or drop.
COMPOUNDS: tuple[str, ...] = (
    "klubmesterskab",
    "tårnslutspil",
    "toldkammeret",
    "æblemost",
    "messingorkester",
    "glasværksted",
    "håndpresse",
    "trykpresse",
    "blæretang",
    "lastcykel",
    "strikkeopskrift",
    "vejrfløje",
    "sognehavn",
    "fergelejet",
    "færgelejet",
    "tørvestykket",
    "natfærge",
    "tidevandsbassin",
)


def aliases_for(key: str) -> tuple[str, ...]:
    for entry in GAZETTEER:
        if entry.key == key:
            return entry.aliases
    raise KeyError(key)
