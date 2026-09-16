"""Tiny ASCII table helper. Stdlib only."""

from __future__ import annotations

from typing import Sequence


def format_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    widths = [len(header) for header in headers]
    str_rows = [[str(cell) for cell in row] for row in rows]
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def _fmt(cells: Sequence[str]) -> str:
        return "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells)) + " |"

    rule = "|-" + "-|-".join("-" * width for width in widths) + "-|"
    lines = [_fmt(headers), rule]
    lines.extend(_fmt(row) for row in str_rows)
    return "\n".join(lines)
