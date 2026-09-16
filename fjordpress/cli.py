"""Command-line entry for the Vesterklit study kit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Sequence

from .corpus import all_articles, validate_corpus
from .csvio import write_rows
from .entities import retention_table
from .fixtures import hops_for_all, write_fixtures
from .ledger import build_ledger, summarise_ledger
from .lexicon import coverage_report
from .packing import (
    DEFAULT_TEXT_MAX_LENGTH,
    WordTokenCounter,
    pack_article,
    pack_like_translate_back,
    packing_stats,
)
from .paths import generated_dir, output_dir
from .report import render_html, render_text, write_html, write_text
from .schemas import SCHEMA_CATALOG, script_io_notes


def _print(text: str) -> None:
    sys.stdout.write(text if text.endswith("\n") else text + "\n")


def cmd_corpus(_args: argparse.Namespace) -> int:
    problems = validate_corpus()
    if problems:
        for problem in problems:
            _print(f"PROBLEM: {problem}")
        return 1
    _print(f"{len(all_articles())} Vesterklit articles, alignments ok.")
    for art in all_articles():
        _print(
            f"  {art.article_id}  {len(art.danish_sentences):2d} sents  "
            f"{art.section:<10}  {art.title_da}"
        )
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    budget = args.budget
    _print(f"Packing Danish sources with word-token budget {budget}")
    _print(
        f"(2023 translate.py used {DEFAULT_TEXT_MAX_LENGTH} subword pieces; "
        "the gazette is too short for that to split anything.)"
    )
    _print("")
    for art in all_articles():
        windows = pack_article(art.danish, text_max_length=budget)
        back = pack_like_translate_back(art.danish, max_length=max(budget, 80))
        stats = packing_stats(windows)
        _print(
            f"{art.article_id}: {stats['n_windows']} window(s), "
            f"{stats['n_sentences']} pieces, "
            f"mean budget {stats['mean_budget']:.1f}"
        )
        if args.verbose:
            for i, window in enumerate(windows):
                _print(f"    w{i} [{window.token_budget}] {window.text[:140]}")
            if len(back) != len(windows):
                _print(f"    translate_back-style windows: {len(back)}")
    return 0


def cmd_hops(args: argparse.Namespace) -> int:
    records = hops_for_all(pack_budget=args.budget)
    for rec in records:
        _print(f"## {rec.article_id}")
        _print(f"gloss DA coverage {rec.gloss_coverage_da:.3f}  "
               f"OOV={len(rec.gloss_unknown_da)}")
        _print(f"oracle EN summary: {rec.english_summary_oracle}")
        _print(f"oracle DA back:    {rec.danish_back_oracle}")
        _print("")
    if args.json:
        payload = [
            {
                "id": rec.article_id,
                "gloss_coverage_da": rec.gloss_coverage_da,
                "oov_da": rec.gloss_unknown_da,
                "oracle_back": rec.danish_back_oracle,
                "gloss_back": rec.danish_back_gloss,
            }
            for rec in records
        ]
        _print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_ledger(args: argparse.Namespace) -> int:
    articles = list(all_articles())
    records = hops_for_all(pack_budget=args.budget)
    rows = []
    for rec, art in zip(records, articles):
        rows.extend(build_ledger(rec, art.entities))
    summary = summarise_ledger(rows)
    _print(json.dumps(summary, indent=2))
    if args.write:
        dest = Path(args.write)
        write_rows(dest, [r.as_dict() for r in rows])
        _print(f"wrote {dest}")
    if args.article:
        rec = next(r for r in records if r.article_id == args.article)
        art = next(a for a in articles if a.article_id == args.article)
        table = retention_table(rec.hop_pairs(), art.entities)
        for row in table:
            kept = ",".join(row["kept"]) or "—"
            lost = ",".join(row["lost"]) or "—"
            _print(f"{row['hop']:<22} ret={row['retention']:.2f}  lost={lost}  kept={kept}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    articles = list(all_articles())
    records = hops_for_all(pack_budget=args.budget)
    rows: List = []
    for rec, art in zip(records, articles):
        rows.extend(build_ledger(rec, art.entities))
    text = render_text(records, articles, rows)
    html = render_html(records, articles, rows)
    if args.stdout:
        _print(text)
    dest_dir = Path(args.out) if args.out else output_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    write_text(dest_dir / "vesterklit-lab-notes.txt", records, articles, rows)
    write_html(dest_dir / "vesterklit-lab-notes.html", records, articles, rows)
    # Also keep a committed snapshot when asked.
    if args.snapshot:
        snap = generated_dir()
        write_text(snap / "vesterklit-lab-notes.txt", records, articles, rows)
        write_html(snap / "vesterklit-lab-notes.html", records, articles, rows)
        _print(f"snapshot -> {snap}")
    _print(f"report -> {dest_dir}")
    # silence unused if someone imports render results
    _ = (text, html)
    return 0


def cmd_fixtures(args: argparse.Namespace) -> int:
    dest = Path(args.out) if args.out else None
    written = write_fixtures(dest, pack_budget=args.budget)
    for name, path in written.items():
        _print(f"{name:<16} {path}")
    return 0


def cmd_lexicon(_args: argparse.Namespace) -> int:
    texts = [art.danish for art in all_articles()]
    report = coverage_report(texts, danish=True)
    _print(f"tokens={report['n_tokens']}  glossed={report['n_glossed']}  "
           f"coverage={report['coverage']:.3f}  "
           f"unknown types={report['n_unknown_types']}")
    unknown = report["unknown_types"]
    if unknown:
        _print("OOV types:")
        for tok in unknown:
            _print(f"  {tok}")
    return 0


def cmd_schemas(_args: argparse.Namespace) -> int:
    for name, cols in SCHEMA_CATALOG.items():
        _print(f"{name}: {', '.join(cols)}")
    _print("")
    _print("Script scars")
    for note in script_io_notes():
        _print(f"  - {note}")
    return 0


def cmd_counter(args: argparse.Namespace) -> int:
    """Show the two 2023 length notions on one sentence."""
    text = args.text or all_articles()[0].danish_sentences[0]
    words = WordTokenCounter().count(text)
    from .packing import ApproxSubwordCounter, CharPlusOneCounter

    chars = CharPlusOneCounter().count(text)
    approx = ApproxSubwordCounter().count(text)
    _print(f"text: {text}")
    _print(f"word tokens:     {words}")
    _print(f"char+1 (long-sentence splitter): {chars}")
    _print(f"approx subword ×1.3: {approx}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fjordpress",
        description="Offline study kit for the 2023 ITU Danish silver-label pipeline.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("corpus", help="validate and list the gazette")
    p.set_defaults(func=cmd_corpus)

    p = sub.add_parser("pack", help="pack gazette articles into 2023-style windows")
    p.add_argument("--budget", type=int, default=40)
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_pack)

    p = sub.add_parser("hops", help="run oracle and gloss hops")
    p.add_argument("--budget", type=int, default=40)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_hops)

    p = sub.add_parser("ledger", help="entity retention and ROUGE ledger")
    p.add_argument("--budget", type=int, default=40)
    p.add_argument("--write", metavar="CSV")
    p.add_argument("--article", metavar="ID")
    p.set_defaults(func=cmd_ledger)

    p = sub.add_parser("report", help="write text and HTML lab notes")
    p.add_argument("--budget", type=int, default=40)
    p.add_argument("--out", metavar="DIR")
    p.add_argument("--snapshot", action="store_true", help="also write docs/generated/")
    p.add_argument("--stdout", action="store_true")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("fixtures", help="write 2023-shaped sample CSVs")
    p.add_argument("--budget", type=int, default=40)
    p.add_argument("--out", metavar="DIR")
    p.set_defaults(func=cmd_fixtures)

    p = sub.add_parser("lexicon", help="print DA→EN coverage on the gazette")
    p.set_defaults(func=cmd_lexicon)

    p = sub.add_parser("schemas", help="print 2023 CSV contracts and scars")
    p.set_defaults(func=cmd_schemas)

    p = sub.add_parser("counter", help="compare the two 2023 length notions")
    p.add_argument("--text")
    p.set_defaults(func=cmd_counter)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return int(args.func(args))
