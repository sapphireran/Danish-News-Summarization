"""Walk the sample CSVs the same way the root scripts walk a full dump.

No model weights are loaded. English and Danish strings already live in
``examples/sample_data/`` as author-written fixtures. This program:

1. Validates every stage file.
2. Packs each Danish body as ``translate.py`` would before OPUS-MT.
3. Assigns labeled rows to train/validation/test with a stable hash.
4. Prints a stage report.

It can also rewrite the ``04_*.csv`` splits from the labeled file when
``--refresh-splits`` is passed. The committed splits were generated that way.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from examples.schemas import (
    LABELED_COLUMNS,
    SPLIT_COLUMNS,
    validate_csv,
    validate_sample_dir,
    write_csv,
)
from examples.text_chunking import pack_article

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"
MARIAN_BUDGET = int(512 * 0.9)
T5_BUDGET = 512


def stable_bucket(ident: str) -> float:
    """Return a deterministic number in ``[0, 1)`` from an id string."""
    digest = hashlib.sha256(ident.encode("utf-8")).digest()
    return digest[0] / 256.0


def split_labeled_rows(
    rows: Sequence[Dict[str, str]],
    *,
    train_cut: float = 0.80,
    validation_cut: float = 0.90,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
    train: List[Dict[str, str]] = []
    validation: List[Dict[str, str]] = []
    test: List[Dict[str, str]] = []
    for row in rows:
        score = stable_bucket(row["id"])
        if score < train_cut:
            train.append(row)
        elif score < validation_cut:
            validation.append(row)
        else:
            test.append(row)
    return train, validation, test


def _print_table(rows: Iterable[Tuple[str, object]]) -> None:
    width = max(len(name) for name, _ in rows)
    for name, value in rows:
        print(f"  {name:<{width}}  {value}")


def report_chunking(labeled_rows: Sequence[Dict[str, str]]) -> List[Tuple[str, int]]:
    stats = []
    print("Packed Danish bodies (Marian-style 460-token budget, word estimator):")
    for row in labeled_rows:
        chunks = pack_article(row["body"], MARIAN_BUDGET)
        stats.append((row["id"], len(chunks)))
        preview = chunks[0][:72] + ("…" if len(chunks[0]) > 72 else "")
        print(f"  - {row['id']}: {len(chunks)} chunk(s); first: {preview}")
    return stats


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-dir",
        type=Path,
        default=SAMPLE_DIR,
        help="Directory of stage CSVs (default: examples/sample_data)",
    )
    parser.add_argument(
        "--refresh-splits",
        action="store_true",
        help="Rewrite 04_train/validation/test CSVs from 03_labeled_dataset.csv",
    )
    args = parser.parse_args(argv)

    counts = validate_sample_dir(args.sample_dir)
    print("Validated sample CSVs:")
    _print_table(sorted(counts.items()))

    labeled = validate_csv(
        args.sample_dir / "03_labeled_dataset.csv",
        LABELED_COLUMNS,
        stage="labeled",
    )
    print()
    report_chunking(labeled)

    train, validation, test = split_labeled_rows(labeled)
    print()
    print("Stable 80/10/10 hash split of labeled ids:")
    _print_table(
        [
            ("train", ", ".join(row["id"] for row in train) or "(empty)"),
            ("validation", ", ".join(row["id"] for row in validation) or "(empty)"),
            ("test", ", ".join(row["id"] for row in test) or "(empty)"),
        ]
    )

    if args.refresh_splits:
        write_csv(args.sample_dir / "04_train_dataset.csv", train, SPLIT_COLUMNS)
        write_csv(args.sample_dir / "04_validation_dataset.csv", validation, SPLIT_COLUMNS)
        write_csv(args.sample_dir / "04_test_dataset.csv", test, SPLIT_COLUMNS)
        print()
        print("Wrote 04_*.csv from the hash split.")

    t5_chunks = sum(len(pack_article(row["body"], T5_BUDGET)) for row in labeled)
    print()
    print(f"T5-style 512 budget would also emit {t5_chunks} chunk(s) across {len(labeled)} articles.")
    print("Demo finished without loading translation or summarization weights.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
