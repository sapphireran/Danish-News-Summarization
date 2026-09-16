"""Tiny CSV helpers that do not require pandas.

The original GPU scripts use ``pandas.read_csv`` / ``to_csv``. Examples and
tests use the standard library so they run in a bare Python 3.12 image.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List, Mapping, Sequence


def read_csv(path: Path | str) -> List[dict]:
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path | str, rows: Sequence[Mapping[str, object]], fieldnames: Iterable[str]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    names = list(fieldnames)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})
    return path
