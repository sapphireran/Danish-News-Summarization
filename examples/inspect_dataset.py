#!/usr/bin/env python3
"""Print length stats for a labeled or split CSV.

Useful before finetune.py: empty rows, duplicate ids, and summaries that
are long relative to the 128-token label cap (here approximated with
whitespace words, not the mT5 tokenizer).

    python3 examples/inspect_dataset.py --path examples/sample_data/03_labeled_sample.csv
"""

from __future__ import annotations

import argparse
import statistics
from pathlib import Path

from chunking import simple_sent_tokenize, window_stats
from csv_util import read_rows
from schema import infer_stage_from_filename

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATH = REPO_ROOT / "examples" / "sample_data" / "03_labeled_sample.csv"

# finetune.py truncates summaries at 128 mT5 tokens. A word count above
# this is only a hint, not a tokenizer measurement.
LABEL_WORD_HINT = 128
BODY_WORD_HINT = 1024


def _median(values: list[int]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def _body_column(header: list[str]) -> str:
    if "body" in header:
        return "body"
    if "article text" in header:
        return "article text"
    raise ValueError("CSV needs a 'body' or 'article text' column")


def inspect(path: Path, text_max_length: int) -> dict[str, object]:
    header, rows = read_rows(path)
    body_column = _body_column(header)
    has_summary = "summary" in header

    bodies = [row.get(body_column, "") for row in rows]
    summaries = [row.get("summary", "") for row in rows] if has_summary else []
    ids = [row.get("id", "").strip() for row in rows]

    body_chars = [len(text) for text in bodies]
    body_words = [len(text.split()) for text in bodies]
    body_sents = [len(simple_sent_tokenize(text)) for text in bodies]
    summary_chars = [len(text) for text in summaries]
    summary_words = [len(text.split()) for text in summaries]

    duplicate_ids = sorted({article_id for article_id in ids if article_id and ids.count(article_id) > 1})
    empty_body = sum(1 for text in bodies if not text.strip())
    empty_summary = sum(1 for text in summaries if not text.strip()) if has_summary else 0
    long_labels = sum(1 for count in summary_words if count > LABEL_WORD_HINT)
    long_bodies = sum(1 for count in body_words if count > BODY_WORD_HINT)

    chunk_windows = [window_stats(text, text_max_length)["windows"] for text in bodies if text.strip()]

    return {
        "path": str(path),
        "rows": len(rows),
        "unique_ids": len({article_id for article_id in ids if article_id}),
        "duplicate_ids": duplicate_ids,
        "empty_body": empty_body,
        "empty_summary": empty_summary,
        "body_chars_min": min(body_chars) if body_chars else 0,
        "body_chars_median": _median(body_chars),
        "body_chars_max": max(body_chars) if body_chars else 0,
        "body_words_median": _median(body_words),
        "body_sents_median": _median(body_sents),
        "summary_chars_median": _median(summary_chars) if has_summary else None,
        "summary_words_median": _median(summary_words) if has_summary else None,
        "summaries_over_128_words": long_labels,
        "bodies_over_1024_words": long_bodies,
        "chunk_windows_median": _median(chunk_windows) if chunk_windows else 0,
        "inferred_stage": infer_stage_from_filename(path.name),
    }


def format_report(stats: dict[str, object]) -> str:
    lines = [
        f"path: {stats['path']}",
        f"stage guess: {stats['inferred_stage']}",
        f"rows: {stats['rows']}",
        f"unique ids: {stats['unique_ids']}",
        f"duplicate ids: {stats['duplicate_ids'] or 'none'}",
        f"empty body rows: {stats['empty_body']}",
        f"empty summary rows: {stats['empty_summary']}",
        (
            "body chars: "
            f"min={stats['body_chars_min']} "
            f"median={stats['body_chars_median']:.0f} "
            f"max={stats['body_chars_max']}"
        ),
        f"body words median: {stats['body_words_median']:.1f}",
        f"body sentences median: {stats['body_sents_median']:.1f}",
        f"chunk windows median (char budget {default_budget_label()}): {stats['chunk_windows_median']:.1f}",
        f"bodies over ~1024 words (hint): {stats['bodies_over_1024_words']}",
    ]
    if stats["summary_chars_median"] is not None:
        lines.extend(
            [
                f"summary chars median: {stats['summary_chars_median']:.0f}",
                f"summary words median: {stats['summary_words_median']:.1f}",
                f"summaries over ~128 words (hint): {stats['summaries_over_128_words']}",
            ]
        )
    return "\n".join(lines)


def default_budget_label() -> str:
    from chunking import default_text_max_length

    return str(default_text_max_length())


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    parser.add_argument(
        "--text-max-length",
        type=int,
        default=None,
        help="chunking budget for the window-count stat (default: int(512 * 0.9))",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    from chunking import default_text_max_length

    args = parse_args(argv)
    budget = args.text_max_length if args.text_max_length is not None else default_text_max_length()
    print(format_report(inspect(args.path, budget)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
