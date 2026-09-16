#!/usr/bin/env python3
"""Walk the committed example snapshots the way the 2023 pipeline would.

No OPUS-MT, T5, or mT5 is loaded. The script checks that:

* each CSV matches the documented schema
* ids are unique and align across stages
* train / validation / test are a partition of the corpus
* the long harbor article (dn-006) actually packs into more than one chunk
  under a small word budget, the same algorithm the root scripts use

Pass ``--json path`` to write a machine-readable report.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

from corpus import ARTICLES, by_id  # noqa: E402
from schema import (  # noqa: E402
    STAGE_FILES,
    SchemaError,
    columns_for,
    has_danish_letters,
    validate_headers,
    validate_row,
)
from text_chunking import default_encode_length, report_chunks  # noqa: E402

DATA_DIR = EXAMPLES_DIR / "data"

# Small on purpose: the example articles are short, and we want dn-006 to
# split so the report shows the packer doing work.
DEMO_BUDGET = 28


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_stage(data_dir: Path, stage_key: str, schema_stage: str) -> list[dict[str, str]]:
    path = data_dir / STAGE_FILES[stage_key]
    if not path.is_file():
        raise FileNotFoundError(
            f"missing {path}. Run: python examples/export_sample_csvs.py"
        )
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        validate_headers(schema_stage, reader.fieldnames or [])
        rows = list(reader)
    for row in rows:
        validate_row(schema_stage, row)
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SchemaError(f"{path.name} has duplicate ids")
    return rows


def align_ids(*id_lists: list[str]) -> None:
    baseline = id_lists[0]
    for other in id_lists[1:]:
        if set(other) != set(baseline):
            raise SchemaError(
                f"id sets diverge: {sorted(set(other) ^ set(baseline))}"
            )


def partition_ok(train: list[str], val: list[str], test: list[str], all_ids: list[str]) -> None:
    combined = train + val + test
    if len(combined) != len(set(combined)):
        raise SchemaError("train/validation/test ids overlap")
    if set(combined) != set(all_ids):
        raise SchemaError(
            f"splits do not cover corpus: {sorted(set(all_ids) ^ set(combined))}"
        )


def danish_ok(rows: list[dict[str, str]], column: str, label: str) -> None:
    if not any(has_danish_letters(row[column]) for row in rows):
        raise SchemaError(f"{label} has no Danish letters in {column!r}")


def run_report(data_dir: Path, budget: int = DEMO_BUDGET) -> dict:
    raw = load_stage(data_dir, "raw", "raw")
    translated = load_stage(data_dir, "translated", "translated")
    summarized = load_stage(data_dir, "summarized", "summarized")
    labeled = load_stage(data_dir, "labeled", "labeled")
    train = load_stage(data_dir, "train", "finetune")
    validation = load_stage(data_dir, "validation", "finetune")
    test = load_stage(data_dir, "test", "finetune")
    predictions = load_stage(data_dir, "predictions", "predictions")

    raw_ids = [row["id"] for row in raw]
    align_ids(
        raw_ids,
        [row["id"] for row in translated],
        [row["id"] for row in summarized],
        [row["id"] for row in labeled],
        [row["id"] for row in predictions],
    )
    partition_ok(
        [row["id"] for row in train],
        [row["id"] for row in validation],
        [row["id"] for row in test],
        raw_ids,
    )

    danish_ok(raw, "article text", "raw")
    danish_ok(labeled, "body", "labeled")
    danish_ok(labeled, "summary", "labeled")

    catalog = by_id()
    if set(catalog) != set(raw_ids):
        raise SchemaError("CSV ids do not match corpus.py")

    # Body must stay the original Danish article at every stage after raw.
    for row in translated + summarized + labeled:
        if row["body"] != catalog[row["id"]].body_da:
            raise SchemaError(f"{row['id']} body drifted from corpus.py")

    chunk_reports = []
    for article in ARTICLES:
        report = report_chunks(article.id, article.body_da, budget)
        chunk_reports.append(
            {
                "id": report.article_id,
                "n_sentences": report.n_sentences,
                "n_chunks": report.n_chunks,
                "chunk_lengths": list(report.chunk_lengths),
                "chunks": list(report.chunks),
            }
        )

    long = next(item for item in chunk_reports if item["id"] == "dn-006")
    if long["n_chunks"] < 2:
        raise SchemaError(
            f"dn-006 should pack into 2+ chunks at budget {budget}, "
            f"got {long['n_chunks']}"
        )
    if any(length > budget for length in long["chunk_lengths"]):
        raise SchemaError("dn-006 produced a chunk over the demo budget")

    return {
        "n_articles": len(raw_ids),
        "ids": raw_ids,
        "splits": {
            "train": [row["id"] for row in train],
            "validation": [row["id"] for row in validation],
            "test": [row["id"] for row in test],
        },
        "schemas": {
            key: list(columns_for(stage))
            for key, stage in (
                ("raw", "raw"),
                ("translated", "translated"),
                ("summarized", "summarized"),
                ("labeled", "labeled"),
                ("finetune", "finetune"),
                ("predictions", "predictions"),
            )
        },
        "chunk_budget": budget,
        "encode": "whitespace words + 2 special tokens",
        "chunk_reports": chunk_reports,
        "notes": {
            article.id: article.notes
            for article in ARTICLES
            if article.notes
        },
    }


def format_human(report: dict) -> str:
    lines = [
        "Toy labeling pipeline (schemas + chunking, no model weights)",
        f"articles: {report['n_articles']}  ids: {' '.join(report['ids'])}",
        (
            "splits: "
            f"train={report['splits']['train']} "
            f"val={report['splits']['validation']} "
            f"test={report['splits']['test']}"
        ),
        f"chunk budget: {report['chunk_budget']} ({report['encode']})",
        "",
        f"{'id':<8} {'sent':>4} {'chk':>4}  lengths",
        "-" * 40,
    ]
    for item in report["chunk_reports"]:
        lengths = ",".join(str(n) for n in item["chunk_lengths"])
        lines.append(
            f"{item['id']:<8} {item['n_sentences']:>4} {item['n_chunks']:>4}  {lengths}"
        )
    lines.append("")
    lines.append("dn-006 chunks (harbor article):")
    harbor = next(item for item in report["chunk_reports"] if item["id"] == "dn-006")
    for index, chunk in enumerate(harbor["chunks"], start=1):
        preview = chunk if len(chunk) <= 160 else chunk[:157] + "..."
        lines.append(f"  [{index}] ({harbor['chunk_lengths'][index - 1]} tok) {preview}")
    lines.append("")
    lines.append("All stage schemas and id alignments checked out.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--budget", type=int, default=DEMO_BUDGET)
    parser.add_argument("--json", type=Path, default=None, dest="json_path")
    args = parser.parse_args()
    report = run_report(args.data_dir, args.budget)
    print(format_human(report))
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\nwrote {args.json_path}")


if __name__ == "__main__":
    main()
