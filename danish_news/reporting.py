"""Plain-text and Markdown tables for the example scripts."""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence


def markdown_table(
    rows: Sequence[Mapping[str, object]],
    columns: Sequence[str] | None = None,
    *,
    float_digits: int = 3,
) -> str:
    """Render a GitHub-flavored Markdown table."""
    if not rows:
        return "_no rows_"
    headers = list(columns) if columns is not None else list(rows[0].keys())
    header_line = "| " + " | ".join(headers) + " |"
    rule_line = "| " + " | ".join("---" for _ in headers) + " |"
    body = [header_line, rule_line]
    for row in rows:
        cells = [_format_cell(row.get(column, ""), float_digits) for column in headers]
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join(body)


def pad_columns(rows: Sequence[Mapping[str, object]], columns: Sequence[str]) -> str:
    """Render an aligned monospaced table for terminal output."""
    if not rows:
        return "(no rows)"
    string_rows = [
        [_format_cell(row.get(column, ""), 3) for column in columns] for row in rows
    ]
    widths = [len(column) for column in columns]
    for row in string_rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    header = "  ".join(column.ljust(widths[index]) for index, column in enumerate(columns))
    rule = "  ".join("-" * widths[index] for index in range(len(columns)))
    lines = [header, rule]
    for row in string_rows:
        lines.append(
            "  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row))
        )
    return "\n".join(lines)


def _format_cell(value: object, float_digits: int) -> str:
    if isinstance(value, float):
        if value != value:  # NaN
            return "nan"
        return f"{value:.{float_digits}f}"
    if value is None:
        return ""
    return str(value)


def iter_percent(values: Iterable[float]) -> list[str]:
    return [f"{100.0 * value:.1f}%" for value in values]
