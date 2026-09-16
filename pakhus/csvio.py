"""Stdlib CSV helpers. The course scripts use pandas; the lab does not."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Sequence


def read_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_dicts(
    path: Path,
    rows: Sequence[dict[str, object]],
    fieldnames: Sequence[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows and not fieldnames:
        raise ValueError(f"no rows and no fieldnames for {path}")
    names = list(fieldnames) if fieldnames is not None else list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in names})


def write_table(
    path: Path, header: Sequence[str], rows: Iterable[Sequence[object]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(list(header))
        for row in rows:
            writer.writerow(list(row))
