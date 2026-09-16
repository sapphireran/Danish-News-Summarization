#!/usr/bin/env python3
"""Walk the silver-label file contracts without OPUS-MT or T5.

Two modes:

* ``--generate`` (default) reads a source dump shaped like
  ``sample_articles.csv`` and writes translated / summarized / labeled
  CSVs plus optional fine-tune splits. Translation and summarization are
  **extractive stubs** so the column names and joins can be tested on a
  laptop.
* ``--replay-fixtures`` copies the committed aligned CSVs into the
  output directory. Use that when you want the hand-written English
  columns instead of the stubs.

Neither mode is the 2023 GPU pipeline. See docs/pipeline.md.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from text_lib import (
    DATA_DIR,
    lead_n_sentences,
    pack_sentences,
    read_csv,
    split_rows,
    write_csv,
)


STAGE_COLUMNS = {
    "source": ("id", "article text"),
    "translated": ("id", "body", "translated"),
    "summarized": ("id", "body", "translated", "summary"),
    "labeled": ("id", "body", "summary"),
}


def stub_translate_da_en(danish: str) -> str:
    """Mark a Danish string as a fake English hop.

    A real run would call OPUS-MT. Keeping the Danish text makes the
    dry-run readable and keeps ids aligned for later overlap checks.
    """
    return "[stub-en] " + danish


def stub_summarize_en(english: str, sentences: int, max_tokens: int) -> str:
    """Lead-N on each packed window, then join — the summary.py shape."""
    windows = pack_sentences(english, max_tokens, split_overlong=True)
    if not windows:
        return lead_n_sentences(english, sentences)
    pieces = [lead_n_sentences(window.as_text(), sentences) for window in windows]
    return " ".join(piece for piece in pieces if piece)


def stub_translate_en_da(english_summary: str, danish_body: str, sentences: int) -> str:
    """Drop the stub prefix if present; otherwise fall back to a Danish lead."""
    text = english_summary
    if text.startswith("[stub-en] "):
        text = text[len("[stub-en] ") :]
    # After generate-mode summarization the text is still Danish lead-N.
    if text:
        return text
    return lead_n_sentences(danish_body, sentences)


def generate(source_rows: list[dict[str, str]], sentences: int, max_tokens: int) -> dict[str, list[dict[str, str]]]:
    translated_rows = []
    summarized_rows = []
    labeled_rows = []
    for row in source_rows:
        article_id = row.get("id", "")
        body = row.get("article text") or row.get("body") or ""
        translated = stub_translate_da_en(body)
        english_summary = stub_summarize_en(translated, sentences=sentences, max_tokens=max_tokens)
        danish_summary = stub_translate_en_da(english_summary, body, sentences=sentences)
        translated_rows.append({"id": article_id, "body": body, "translated": translated})
        summarized_rows.append(
            {
                "id": article_id,
                "body": body,
                "translated": translated,
                "summary": english_summary,
            }
        )
        labeled_rows.append({"id": article_id, "body": body, "summary": danish_summary})
    return {
        "translated": translated_rows,
        "summarized": summarized_rows,
        "labeled": labeled_rows,
    }


def replay() -> dict[str, list[dict[str, str]]]:
    return {
        "translated": read_csv(DATA_DIR / "sample_translated.csv"),
        "summarized": read_csv(DATA_DIR / "sample_summarized.csv"),
        "labeled": read_csv(DATA_DIR / "sample_labeled.csv"),
    }


def write_stages(output_dir: Path, stages: dict[str, list[dict[str, str]]]) -> dict[str, str]:
    mapping = {
        "translated": output_dir / "translated_articles.csv",
        "summarized": output_dir / "summarized_file_ml80_rp5.0.csv",
        "labeled": output_dir / "labeled_dataset_ml80_rp5.0.csv",
    }
    written = {}
    for name, path in mapping.items():
        write_csv(path, stages[name], STAGE_COLUMNS[name])
        written[name] = str(path)
    return written


def maybe_split(
    labeled_rows: list[dict[str, str]],
    output_dir: Path,
    train: float,
    validation: float,
    test: float,
    seed: int,
) -> dict[str, dict[str, int | str]]:
    buckets = split_rows(
        labeled_rows,
        train=train,
        validation=validation,
        test=test,
        seed=seed,
    )
    split_dir = output_dir / "datasets"
    written = {}
    for name, rows in buckets.items():
        path = split_dir / f"{name}_dataset.csv"
        write_csv(path, rows, ("id", "body", "summary"))
        written[name] = {"path": str(path), "rows": len(rows)}
    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[1] / "configs" / "pipeline.example.json"),
        help="Unused by the stub logic; recorded in the run report",
    )
    parser.add_argument("--input", default=str(DATA_DIR / "sample_articles.csv"))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--replay-fixtures", action="store_true")
    parser.add_argument("--sentences", type=int, default=2, help="Lead-N for the generate stub")
    parser.add_argument("--max-tokens", type=int, default=80, help="Packing budget for generate")
    parser.add_argument("--split", action="store_true", help="Also write datasets/*.csv")
    parser.add_argument("--train", type=float, default=0.7)
    parser.add_argument("--validation", type=float, default=0.2)
    parser.add_argument("--test", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=2023)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = Path(args.output_dir)
    if output_dir.exists():
        # Keep reruns deterministic: replace the previous dry-run tree.
        for child in output_dir.glob("**/*"):
            if child.is_file() and child.suffix == ".csv":
                child.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)

    source_path = Path(args.input)
    source_rows = read_csv(source_path)
    if not source_rows:
        print(f"No source rows in {source_path}", file=sys.stderr)
        return 1

    if args.replay_fixtures:
        stages = replay()
        mode = "replay-fixtures"
        shutil.copy2(DATA_DIR / "sample_articles.csv", output_dir / "sample_articles.csv")
    else:
        stages = generate(source_rows, sentences=args.sentences, max_tokens=args.max_tokens)
        mode = "generate"
        write_csv(output_dir / "10000_articles_without_linebreaks.csv", source_rows, STAGE_COLUMNS["source"])

    written = write_stages(output_dir, stages)
    splits = None
    if args.split:
        splits = maybe_split(
            stages["labeled"],
            output_dir,
            train=args.train,
            validation=args.validation,
            test=args.test,
            seed=args.seed,
        )

    report = {
        "mode": mode,
        "config": args.config,
        "input": str(source_path),
        "output_dir": str(output_dir),
        "rows": len(source_rows),
        "files": written,
        "splits": splits,
        "stub": {
            "sentences": args.sentences,
            "max_tokens": args.max_tokens,
            "translation": "identity with [stub-en] prefix" if mode == "generate" else "hand-written fixtures",
        },
    }

    report_path = output_dir / "dry_run_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"mode:  {mode}")
        print(f"rows:  {len(source_rows)}")
        for name, path in written.items():
            print(f"{name:12} {path}")
        if splits:
            for name, info in splits.items():
                print(f"split {name:12} {info['rows']:4d}  {info['path']}")
        print(f"report: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
