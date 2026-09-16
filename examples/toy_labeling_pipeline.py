#!/usr/bin/env python3
"""CPU stand-in for translate → summarize → translate-back → split.

The course scripts need OPUS-MT, T5, and a GPU. This walkthrough does not.
It reads the fictional raw dump and writes:

* an *extractive* labeled CSV (first two Danish sentences)
* train/validation/test splits with the same ids as examples/data/finetune/
* a side-by-side comparison against the hand-written pivot labels

Outputs land in examples/output/ so a rerun cannot clobber committed samples.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.lib.extractive_summary import extractive_summary  # noqa: E402
from examples.lib.sample_corpus import (  # noqa: E402
    TEST_IDS,
    TRAIN_IDS,
    VALIDATION_IDS,
    by_id,
)
from examples.lib.schema import looks_danish  # noqa: E402

EXAMPLES = Path(__file__).resolve().parent
DATA = EXAMPLES / "data"
OUTPUT = EXAMPLES / "output"


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _overlap(a: str, b: str) -> float:
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=DATA / "raw_danish_articles.csv")
    parser.add_argument("--pivot", type=Path, default=DATA / "labeled_danish.csv")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--max-sentences", type=int, default=2)
    args = parser.parse_args()

    raw_rows = _read(args.raw)
    if not raw_rows:
        raise SystemExit(f"no rows in {args.raw}")

    labeled = []
    for row in raw_rows:
        summary = extractive_summary(
            row["article text"],
            max_sentences=args.max_sentences,
            language="danish",
        )
        if not looks_danish(summary):
            raise SystemExit(f"extractive summary for {row['id']} does not look Danish")
        labeled.append({"id": row["id"], "body": row["article text"], "summary": summary})

    out_dir = args.output_dir
    _write(out_dir / "labeled_extractive.csv", ["id", "body", "summary"], labeled)

    by_split = {
        "train_dataset.csv": TRAIN_IDS,
        "validation_dataset.csv": VALIDATION_IDS,
        "test_dataset.csv": TEST_IDS,
    }
    labeled_by_id = {row["id"]: row for row in labeled}
    for filename, ids in by_split.items():
        _write(
            out_dir / "finetune" / filename,
            ["id", "body", "summary"],
            [labeled_by_id[i] for i in ids],
        )

    pivot_rows = {row["id"]: row["summary"] for row in _read(args.pivot)}
    comparison = []
    overlaps = []
    for row in labeled:
        pivot = pivot_rows[row["id"]]
        score = _overlap(row["summary"], pivot)
        overlaps.append(score)
        comparison.append(
            {
                "id": row["id"],
                "jaccard": f"{score:.3f}",
                "extractive": row["summary"],
                "pivot_silver": pivot,
            }
        )
    _write(
        out_dir / "extractive_vs_pivot.csv",
        ["id", "jaccard", "extractive", "pivot_silver"],
        comparison,
    )

    mean_overlap = sum(overlaps) / len(overlaps)
    print("toy labeling pipeline OK")
    print(f"  wrote {len(labeled)} extractive rows → {out_dir / 'labeled_extractive.csv'}")
    print(f"  splits {len(TRAIN_IDS)}/{len(VALIDATION_IDS)}/{len(TEST_IDS)} → {out_dir / 'finetune'}")
    print(f"  mean unigram Jaccard vs pivot labels: {mean_overlap:.3f}")
    print("  (low overlap is expected: lede extraction ≠ T5-via-OPUS style)")

    # Guard the committed split ids so a corpus edit cannot silently drift.
    corpus_ids = set(by_id())
    written_ids = {row["id"] for row in labeled}
    if written_ids != corpus_ids:
        raise SystemExit(f"raw CSV ids {sorted(written_ids)} != corpus {sorted(corpus_ids)}")


if __name__ == "__main__":
    main()
