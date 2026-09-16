#!/usr/bin/env python3
"""Run an offline stand-in for the DA→EN→summarize→DA labeling pipeline.

The 2023 scripts need converted OPUS-MT models, a news T5, and usually a GPU.
This example keeps the same stage filenames and column contracts, but it
replaces neural translation and abstractive summarization with:

1. sentence packing (the control flow from ``translate.py``)
2. extractive Danish summarization (a local stand-in for T5 + back-translation)
3. a deterministic train/validation/test split

Hand-written gold files in ``examples/data`` stay untouched. Generated
silver labels go to ``--output-dir`` so you can compare the two.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from examples.extractive_summary import extractive_summarize
from examples.sample_catalog import SAMPLES
from examples.schema import validate_records
from examples.text_chunking import split_into_sentence_batches, word_length


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline(
    max_batch_words: int,
    max_summary_sentences: int,
    max_summary_chars: int,
    output_dir: Path,
) -> dict[str, object]:
    translated_rows: list[dict[str, str]] = []
    summarized_rows: list[dict[str, str]] = []
    labeled_rows: list[dict[str, str]] = []
    batch_counts: dict[str, int] = {}

    for sample in SAMPLES:
        batches = split_into_sentence_batches(sample["body_da"], max_length=max_batch_words)
        batch_counts[sample["id"]] = len(batches)

        # Offline stand-in for DA→EN: keep Danish but record that each batch
        # would have been a separate translator call.
        fake_english = (
            f"[offline-en batches={len(batches)}] " + sample["body_da"]
        )
        silver_summary = extractive_summarize(
            sample["body_da"],
            max_sentences=max_summary_sentences,
            max_chars=max_summary_chars,
        )

        translated_rows.append(
            {
                "id": sample["id"],
                "body": sample["body_da"],
                "translated": fake_english,
            }
        )
        summarized_rows.append(
            {
                "id": sample["id"],
                "body": sample["body_da"],
                "translated": fake_english,
                "summary": silver_summary,
            }
        )
        labeled_rows.append(
            {
                "id": sample["id"],
                "body": sample["body_da"],
                "summary": silver_summary,
            }
        )

    problems = []
    problems.extend(validate_records(translated_rows, "translated_articles"))
    problems.extend(validate_records(summarized_rows, "summarized_english"))
    problems.extend(validate_records(labeled_rows, "labeled_danish"))
    if problems:
        raise RuntimeError("generated rows failed schema checks: " + "; ".join(problems))

    splits = {"train": [], "validation": [], "test": []}
    for sample, labeled in zip(SAMPLES, labeled_rows, strict=True):
        splits[sample["split"]].append(labeled)

    write_csv(output_dir / "translated_articles.csv", ["id", "body", "translated"], translated_rows)
    write_csv(
        output_dir / "summarized_file_ml80_rp5.0.csv",
        ["id", "body", "translated", "summary"],
        summarized_rows,
    )
    write_csv(
        output_dir / "labeled_dataset_ml80_rp5.0.csv",
        ["id", "body", "summary"],
        labeled_rows,
    )
    write_csv(output_dir / "train_dataset.csv", ["id", "body", "summary"], splits["train"])
    write_csv(output_dir / "validation_dataset.csv", ["id", "body", "summary"], splits["validation"])
    write_csv(output_dir / "test_dataset.csv", ["id", "body", "summary"], splits["test"])

    report = {
        "articles": len(SAMPLES),
        "max_batch_words": max_batch_words,
        "max_summary_sentences": max_summary_sentences,
        "max_summary_chars": max_summary_chars,
        "batches_per_article": batch_counts,
        "compression": [
            {
                "id": sample["id"],
                "body_words": word_length(sample["body_da"]),
                "silver_words": word_length(labeled["summary"]),
                "gold_words": word_length(sample["summary_da"]),
                "silver_summary": labeled["summary"],
            }
            for sample, labeled in zip(SAMPLES, labeled_rows, strict=True)
        ],
        "output_dir": str(output_dir),
    }
    (output_dir / "toy_pipeline_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def print_report(report: dict[str, object]) -> None:
    print("Offline toy pipeline")
    print("====================")
    print(f"articles: {report['articles']}")
    print(f"word budget per translation batch: {report['max_batch_words']}")
    print(f"extractive summary: {report['max_summary_sentences']} sentences, {report['max_summary_chars']} chars")
    print()
    print(f"{'id':<22} {'batches':>8} {'src':>5} {'silver':>7} {'gold':>5}")
    batches = report["batches_per_article"]
    for row in report["compression"]:
        print(
            f"{row['id']:<22} {batches[row['id']]:>8} {row['body_words']:>5} "
            f"{row['silver_words']:>7} {row['gold_words']:>5}"
        )
    print()
    print(f"wrote CSVs and report to {report['output_dir']}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-batch-words", type=int, default=40)
    parser.add_argument("--max-summary-sentences", type=int, default=2)
    parser.add_argument("--max-summary-chars", type=int, default=320)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_ROOT / "examples" / "output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = run_pipeline(
        max_batch_words=args.max_batch_words,
        max_summary_sentences=args.max_summary_sentences,
        max_summary_chars=args.max_summary_chars,
        output_dir=args.output_dir,
    )
    print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
