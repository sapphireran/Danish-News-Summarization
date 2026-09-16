"""Command-line entry points used by the examples and README.

    python -m danish_news_summarization.cli stages
    python -m danish_news_summarization.cli schema labeled
    python -m danish_news_summarization.cli chunk --max-length 40
    python -m danish_news_summarization.cli dry-run --out examples/output
    python -m danish_news_summarization.cli export-data --out examples/data
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .chunking import WhitespaceTokenizer, split_article
from .config import PIPELINE_STAGES, STAGE_BY_NAME
from .csv_io import write_csv
from .pipeline import run_dry_pipeline
from .sample_data import SAMPLE_ARTICLES
from .schema import STAGE_COLUMNS, describe_stage, required_columns


def _print_stages() -> int:
    print(f"{'stage':<22} {'script':<24} {'in → out'}")
    print("-" * 78)
    for stage in PIPELINE_STAGES:
        print(f"{stage.name:<22} {stage.script:<24} {stage.input_path} → {stage.output_path}")
        print(f"  {stage.description}")
    return 0


def _print_schema(stage: str) -> int:
    print(describe_stage(stage))
    return 0


def _chunk_articles(max_length: int, article_id: str | None) -> int:
    tokenizer = WhitespaceTokenizer()
    articles = SAMPLE_ARTICLES
    if article_id:
        articles = tuple(article for article in articles if article.id == article_id)
        if not articles:
            print(f"Unknown id {article_id!r}.", file=sys.stderr)
            return 2

    for article in articles:
        chunks = split_article(article.body, max_length, tokenizer)
        print(f"# {article.id}  {article.title}")
        print(f"  words={len(article.body.split())}  windows={len(chunks)}  budget={max_length}")
        for index, chunk in enumerate(chunks, start=1):
            preview = chunk if len(chunk) <= 160 else chunk[:157] + "..."
            print(f"  [{index}/{len(chunks)}] {preview}")
        print()
    return 0


def _dry_run(out_dir: Path, max_length: int, stubs: bool) -> int:
    report = run_dry_pipeline(
        SAMPLE_ARTICLES,
        text_max_length=max_length,
        use_reference_labels=not stubs,
    )
    tables = report.tables()
    out_dir.mkdir(parents=True, exist_ok=True)

    mapping = {
        "raw_articles": "sample_danish_articles.csv",
        "translated": "sample_translated_articles.csv",
        "summarized": "sample_summarized_articles.csv",
        "labeled": "sample_labeled_dataset.csv",
    }
    written = []
    for stage, filename in mapping.items():
        path = write_csv(out_dir / filename, tables[stage], STAGE_COLUMNS[stage])
        written.append(path)

    stats_path = out_dir / "compression_stats.json"
    stats_path.write_text(json.dumps(report.compression_rows(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(stats_path)

    print(f"Wrote {len(written)} artifacts to {out_dir}/ using {report.tokenizer_name}, budget={max_length}.")
    for path in written:
        print(f"  {path}")
    print()
    print(f"{'id':<8} {'da':>5} {'en':>5} {'sum':>5} {'ratio':>6} {'win':>4}")
    for row in report.compression_rows():
        print(
            f"{row['id']:<8} {row['danish_words']:>5} {row['english_words']:>5} "
            f"{row['danish_summary_words']:>5} {row['compression']:>6} {row['translation_windows']:>4}"
        )
    return 0


def _export_data(out_dir: Path) -> int:
    """Write the committed sample CSVs that live under examples/data/."""
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = [article.raw_row for article in SAMPLE_ARTICLES]
    translated = [
        {
            "id": article.id,
            "body": article.body,
            "translated": article.translation,
        }
        for article in SAMPLE_ARTICLES
    ]
    summarized = [
        {
            "id": article.id,
            "body": article.body,
            "translated": article.translation,
            "summary": article.english_summary,
        }
        for article in SAMPLE_ARTICLES
    ]
    labeled = [article.labeled_row for article in SAMPLE_ARTICLES]
    meta = [
        {
            "id": article.id,
            "title": article.title,
            "city": article.city,
            "topic": article.topic,
            "danish_words": len(article.body.split()),
            "english_words": len(article.translation.split()),
        }
        for article in SAMPLE_ARTICLES
    ]

    write_csv(out_dir / "sample_danish_articles.csv", raw, required_columns("raw_articles"))
    write_csv(out_dir / "sample_translated_articles.csv", translated, required_columns("translated"))
    write_csv(out_dir / "sample_summarized_articles.csv", summarized, required_columns("summarized"))
    write_csv(out_dir / "sample_labeled_dataset.csv", labeled, required_columns("labeled"))
    write_csv(
        out_dir / "sample_article_index.csv",
        meta,
        ["id", "title", "city", "topic", "danish_words", "english_words"],
    )
    print(f"Exported {len(SAMPLE_ARTICLES)} articles to {out_dir}/")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="danish-news-summarization")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("stages", help="List the original GPU pipeline stages.")

    schema = sub.add_parser("schema", help="Print the CSV contract for one stage.")
    schema.add_argument("stage", choices=sorted(STAGE_COLUMNS))

    chunk = sub.add_parser("chunk", help="Show packed windows for the sample articles.")
    chunk.add_argument("--max-length", type=int, default=40)
    chunk.add_argument("--id", dest="article_id", default=None)

    dry = sub.add_parser("dry-run", help="Write dry-run CSVs and compression stats.")
    dry.add_argument("--out", type=Path, default=Path("examples/output"))
    dry.add_argument("--max-length", type=int, default=80)
    dry.add_argument(
        "--stubs",
        action="store_true",
        help="Use identity-translate + lead-sentence stubs instead of reference labels.",
    )

    export = sub.add_parser("export-data", help="Write the hand-authored sample CSVs.")
    export.add_argument("--out", type=Path, default=Path("examples/data"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "stages":
        return _print_stages()
    if args.command == "schema":
        return _print_schema(args.stage)
    if args.command == "chunk":
        return _chunk_articles(args.max_length, args.article_id)
    if args.command == "dry-run":
        return _dry_run(args.out, args.max_length, args.stubs)
    if args.command == "export-data":
        return _export_data(args.out)
    parser.error(f"Unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
