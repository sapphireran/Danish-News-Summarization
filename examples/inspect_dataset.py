"""Print length stats and a preview of a pipeline CSV.

Examples:

    python examples/inspect_dataset.py
    python examples/inspect_dataset.py examples/data/sample_labeled_dataset.csv
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.danish_sentences import sent_tokenize, word_tokenize

DEFAULT_PATH = ROOT / "examples" / "data" / "sample_labeled_dataset.csv"
TEXT_COLUMNS = ("article text", "body", "translated", "summary", "reference", "prediction")


def _read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise SystemExit(f"{path} has no header")
        return list(reader.fieldnames), list(reader)


def _stats(values: list[int]) -> str:
    if not values:
        return "n=0"
    return (
        f"n={len(values)} min={min(values)} median={statistics.median(values):.0f} "
        f"mean={statistics.mean(values):.1f} max={max(values)}"
    )


def inspect(path: Path, preview: int) -> None:
    fieldnames, rows = _read(path)
    print(f"file: {path}")
    print(f"columns: {fieldnames}")
    print(f"rows: {len(rows)}")
    if rows and "id" in fieldnames:
        print(f"ids: {', '.join(row['id'] for row in rows)}")

    present = [column for column in TEXT_COLUMNS if column in fieldnames]
    for column in present:
        chars = [len(row[column]) for row in rows]
        words = [len(word_tokenize(row[column])) for row in rows]
        sents = [len(sent_tokenize(row[column])) for row in rows]
        print(f"\n[{column}] characters: {_stats(chars)}")
        print(f"[{column}] words:       {_stats(words)}")
        print(f"[{column}] sentences:   {_stats(sents)}")

    for row in rows[:preview]:
        print("\n" + "=" * 72)
        print(f"id={row.get('id', '?')}")
        for column in present:
            text = row[column].replace("\n", " ")
            snippet = text if len(text) <= 280 else text[:277] + "..."
            print(f"  {column}: {snippet}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", default=str(DEFAULT_PATH))
    parser.add_argument("--preview", type=int, default=2)
    args = parser.parse_args()
    inspect(Path(args.csv_path), args.preview)


if __name__ == "__main__":
    main()
