"""UTF-8 CSV helpers used by the toy scripts.

The 2023 pipeline used pandas. The examples stay on the standard library
so `python -m unittest` works in a bare Cloud Agent image.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping, Sequence

Row = dict[str, str]


def read_csv(path: str | Path) -> list[Row]:
    path = Path(path)
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header row")
        rows: list[Row] = []
        for raw in reader:
            rows.append({key: (value if value is not None else "") for key, value in raw.items()})
        return rows


def write_csv(path: str | Path, rows: Sequence[Mapping[str, str]], fieldnames: Sequence[str]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def ids_of(rows: Iterable[Mapping[str, str]]) -> list[str]:
    return [str(row["id"]) for row in rows]
