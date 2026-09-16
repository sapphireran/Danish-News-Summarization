#!/usr/bin/env python3
"""Walk a stage-0 CSV through the four file formats without any model.

This is a format demo, not a substitute for OPUS-MT / T5. Translation is a
visible `[EN] ...` wrapper, summarization is extractive (first two English
windows), and the Danish label is the first two source sentences.

    python3 examples/toy_pipeline.py \\
        --sample-dir examples/sample_data \\
        --output-dir /tmp/dns-toy

Pass `--replay-gold` to copy the checked-in English/Danish gold fields from
`examples/sample_articles.py` instead of the mocks. That mode is how the
committed sample CSVs are built.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from chunking import default_text_max_length, simple_sent_tokenize, split_article
from csv_util import read_rows, write_rows
from sample_articles import by_id
from schema import (
    REQUIRED_COLUMNS,
    SAMPLE_FILENAMES,
    STAGE_0_ARTICLES,
    STAGE_1_TRANSLATED,
    STAGE_2_SUMMARIZED,
    STAGE_3_LABELED,
)
from validate_csvs import validate_alignment, validate_file

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SAMPLE_DIR = REPO_ROOT / "examples" / "sample_data"


def mock_translate_da_en(danish: str) -> str:
    return f"[EN] {danish}"


def mock_summarize_en(english: str, text_max_length: int) -> str:
    windows = split_article(english, text_max_length=text_max_length)
    if not windows:
        return ""
    # The course script summarizes *each* window. The toy keeps two windows
    # so the output stays short enough to resemble a label.
    pieces = windows[:2]
    first_sentences = []
    for piece in pieces:
        sentences = simple_sent_tokenize(piece)
        first_sentences.extend(sentences[:1] or [piece])
    return " ".join(first_sentences)


def mock_translate_en_da(english_summary: str, danish_source: str) -> str:
    """Drop the `[EN]` wrapper when present; otherwise take two Danish sentences."""
    if english_summary.startswith("[EN] "):
        return english_summary[len("[EN] ") :]
    sentences = simple_sent_tokenize(danish_source)
    return " ".join(sentences[:2])


def gold_fields(article_id: str) -> dict[str, str]:
    article = by_id(article_id)
    return {
        "translated": article["translated"],
        "summary_en": article["summary_en"],
        "summary_da": article["summary_da"],
        "body": article["article_text"],
    }


def run_pipeline(
    stage0_path: Path,
    output_dir: Path,
    text_max_length: int,
    replay_gold: bool,
) -> dict[str, Path]:
    header, rows = read_rows(stage0_path)
    if "id" not in header or "article text" not in header:
        raise ValueError(f"{stage0_path} must have columns id, article text")

    translated_rows = []
    summarized_rows = []
    labeled_rows = []

    for row in rows:
        article_id = row["id"]
        danish = row["article text"]
        if replay_gold:
            gold = gold_fields(article_id)
            english = gold["translated"]
            summary_en = gold["summary_en"]
            summary_da = gold["summary_da"]
        else:
            english = mock_translate_da_en(danish)
            summary_en = mock_summarize_en(english, text_max_length)
            summary_da = mock_translate_en_da(summary_en, danish)

        translated_rows.append({"id": article_id, "body": danish, "translated": english})
        summarized_rows.append(
            {
                "id": article_id,
                "body": danish,
                "translated": english,
                "summary": summary_en,
            }
        )
        labeled_rows.append({"id": article_id, "body": danish, "summary": summary_da})

    output_dir.mkdir(parents=True, exist_ok=True)
    written = {
        STAGE_1_TRANSLATED: output_dir / SAMPLE_FILENAMES[STAGE_1_TRANSLATED],
        STAGE_2_SUMMARIZED: output_dir / SAMPLE_FILENAMES[STAGE_2_SUMMARIZED],
        STAGE_3_LABELED: output_dir / SAMPLE_FILENAMES[STAGE_3_LABELED],
    }
    write_rows(written[STAGE_1_TRANSLATED], REQUIRED_COLUMNS[STAGE_1_TRANSLATED], translated_rows)
    write_rows(written[STAGE_2_SUMMARIZED], REQUIRED_COLUMNS[STAGE_2_SUMMARIZED], summarized_rows)
    write_rows(written[STAGE_3_LABELED], REQUIRED_COLUMNS[STAGE_3_LABELED], labeled_rows)
    return written


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--input", type=Path, help="stage-0 CSV (default: sample_dir/00_articles_sample.csv)")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--text-max-length", type=int, default=default_text_max_length())
    parser.add_argument(
        "--replay-gold",
        action="store_true",
        help="copy English/Danish gold from sample_articles.py instead of mocks",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    stage0 = args.input or (args.sample_dir / SAMPLE_FILENAMES[STAGE_0_ARTICLES])
    written = run_pipeline(
        stage0_path=stage0,
        output_dir=args.output_dir,
        text_max_length=args.text_max_length,
        replay_gold=args.replay_gold,
    )
    issues = []
    staged = {STAGE_0_ARTICLES: stage0, **written}
    for stage, path in written.items():
        issues.extend(validate_file(path, stage))
    issues.extend(validate_alignment(staged))
    for stage, path in written.items():
        print(f"{stage:12} {path}")
    if issues:
        print("validation issues:")
        for issue in issues:
            print(f"  {issue}")
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
