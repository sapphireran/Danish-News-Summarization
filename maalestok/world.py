"""Closed fictional parish used by the almanac fixtures.

Nothing here is scraped news. Names, farms, and roads were invented for this
lab so the 10k Danish dump never has to be committed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Parish:
    name: str
    church: str
    school: str
    dairy: str
    woods: str
    hall: str
    bridge: str
    bus_stop: str
    fields: str
    village: str
    stream: str
    people: tuple[str, ...]


PARISH = Parish(
    name="Blåhøj Sogn",
    church="Blåhøj Kirke",
    school="Sønderholt Skole",
    dairy="Kærholm Mejeri",
    woods="Rævedal Skov",
    hall="Stenholt Hallen",
    bridge="Pilebro",
    bus_stop="Nørreled",
    fields="Havremarken",
    village="Græsbjerg",
    stream="Mosebækken",
    people=(
        "Inge Skovgaard",
        "Morten Bæk",
        "Hanne Friis",
        "Ejvind Holm",
        "Pia Kjeldsen",
        "Ole Nygaard",
    ),
)

# Surface forms the extractor should treat as parish landmarks, not measures.
LANDMARKS = (
    PARISH.church,
    PARISH.school,
    PARISH.dairy,
    PARISH.woods,
    PARISH.hall,
    PARISH.bridge,
    PARISH.bus_stop,
    PARISH.fields,
    PARISH.village,
    PARISH.stream,
)
