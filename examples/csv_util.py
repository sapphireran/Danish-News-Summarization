"""Stdlib CSV helpers shared by the example scripts."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping, Sequence

Row = dict[str, str]


def read_rows(path: Path | str) -> tuple[list[str], list[Row]]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{csv_path}: file has no header row")
        header = list(reader.fieldnames)
        rows = [{key: (row.get(key) or "") for key in header} for row in reader]
    return header, rows


def write_rows(path: Path | str, header: Sequence[str], rows: Iterable[Mapping[str, str]]) -> None:
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(header), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in header})


def column_values(rows: Sequence[Mapping[str, str]], column: str) -> list[str]:
    return [row.get(column, "") for row in rows]
