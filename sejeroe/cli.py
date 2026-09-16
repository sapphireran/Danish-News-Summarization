"""Command-line desk for the Sejerø workbook."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sejeroe.align import align_article
from sejeroe.baseline import baselines_for, comparison_table
from sejeroe.cards import write_cards
from sejeroe.corpus import write_corpus
from sejeroe.fixtures import ARTICLES, article_by_id
from sejeroe.hops import hop_records
from sejeroe.length import pair_lengths
from sejeroe.manchet import score_manchet
from sejeroe.metrics import planted_blind_spots, score_article
from sejeroe.packing import PRESETS, pack_report_rows, pack_text
from sejeroe.paths import DATA_DIR
from sejeroe.report import build_text_report, write_reports
from sejeroe.stylebook import grade
from sejeroe.tokenize import LengthNotion
from sejeroe.validate import require_valid, validate


def _print(text: str) -> None:
    sys.stdout.write(text if text.endswith("\n") else text + "\n")


def cmd_hops(args: argparse.Namespace) -> int:
    target = Path(args.out) if args.out else DATA_DIR
    written = write_corpus(target)
    _print(f"Wrote {len(written)} CSV files under {target}")
    for name, path in written.items():
        _print(f"  {name}: {path}")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    articles = [article_by_id(args.id)] if args.id else list(ARTICLES)
    for article in articles:
        _print(f"# {article.id} {article.headline_da}")
        for row in score_article(article):
            _print(
                f"  {row.text_role:24} slots={row.slot_recall:.2f} "
                f"missing={list(row.missing_slots) or '-'} "
                f"manchet={row.manchet_coverage:.2f} "
                f"quotes={row.quotes_kept}/{row.quotes_total} "
                f"R1-oracle={row.rouge1_vs_oracle:.2f}"
            )
        _print("")
    return 0


def cmd_manchet(args: argparse.Namespace) -> int:
    articles = [article_by_id(args.id)] if args.id else list(ARTICLES)
    for article in articles:
        for role, text in (
            ("body_da", article.body_da),
            ("summary_da", article.summary_da),
            ("oracle_da", article.oracle_da),
        ):
            score = score_manchet(article, text, role)
            _print(
                f"{article.id}  {role:11} coverage={score.coverage:.2f} "
                f"hits={list(score.hits)} misses={list(score.misses) or '-'}"
            )
            _print(f"    {score.lead}")
        _print("")
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    article = article_by_id(args.id) if args.id else ARTICLES[0]
    if args.policy:
        if args.policy not in PRESETS:
            sys.stderr.write(
                f"unknown policy {args.policy!r}; choose from {', '.join(sorted(PRESETS))}\n"
            )
            return 1
        policy = PRESETS[args.policy]
        windows = pack_text(article.body_da, policy)
        _print(
            f"{article.id} policy={policy.name} budget={policy.budget} "
            f"notion={policy.notion.value} windows={len(windows)}"
        )
        for window in windows:
            _print(
                f"  [{window.index}] tokens={window.token_count} "
                f"cut={window.overflow_cut} :: {window.text}"
            )
        return 0
    for row in pack_report_rows(article.body_da):
        _print(
            f"{article.id}  {row['policy']:16} budget={row['budget']:4} "
            f"windows={row['windows']} overflow_cuts={row['overflow_cuts']} "
            f"({row['notion']})"
        )
    return 0


def cmd_length(_: argparse.Namespace) -> int:
    _print(f"{'id':8} {'words da':>8} {'words en':>8} {'w x':>6} {'sub da':>8} {'sub en':>8} {'s x':>6}")
    for article in ARTICLES:
        words = pair_lengths(article, LengthNotion.WORDS)
        pieces = pair_lengths(article, LengthNotion.ROUGH_SUBWORD)
        _print(
            f"{article.id:8} {words.danish:8} {words.english:8} {words.ratio:6.2f} "
            f"{pieces.danish:8} {pieces.english:8} {pieces.ratio:6.2f}"
        )
    return 0


def cmd_walk(args: argparse.Namespace) -> int:
    article = article_by_id(args.id) if args.id else ARTICLES[0]
    _print(f"# {article.id} {article.headline_da}")
    for record in hop_records(article):
        _print(f"\n## {record.hop}  [{record.course_script}]")
        _print(record.note)
        _print(record.text)
    return 0


def cmd_planted(_: argparse.Namespace) -> int:
    for article in ARTICLES:
        for row in planted_blind_spots(article):
            _print(json.dumps(row, ensure_ascii=False))
    return 0


def cmd_report(_: argparse.Namespace) -> int:
    paths = write_reports()
    for name, path in paths.items():
        _print(f"{name}: {path}")
    return 0


def cmd_notes(_: argparse.Namespace) -> int:
    _print(build_text_report())
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    directory = Path(args.out) if args.out else DATA_DIR
    problems = validate(directory)
    if problems:
        for item in problems:
            _print(f"FAIL {item}")
        return 1
    _print("OK Sejerø fixtures and CSV headers")
    return 0


def cmd_baseline(args: argparse.Namespace) -> int:
    articles = [article_by_id(args.id)] if args.id else list(ARTICLES)
    _print(
        f"{'id':8} {'lead1_m':>8} {'silver_m':>9} {'oracle_m':>9} "
        f"{'lead1_s':>8} {'silver_s':>9} {'lead1>sil':>9}"
    )
    for article in articles:
        row = comparison_table(article)
        _print(
            f"{row['article_id']:8} {row['lead1_manchet']:8.2f} {row['silver_manchet']:9.2f} "
            f"{row['oracle_manchet']:9.2f} {row['lead1_slots']:8.2f} {row['silver_slots']:9.2f} "
            f"{str(row['lead1_beats_silver_manchet']):>9}"
        )
        if args.id:
            for item in baselines_for(article):
                _print(f"  {item.name:10} {item.text}")
    return 0


def cmd_gates(args: argparse.Namespace) -> int:
    articles = [article_by_id(args.id)] if args.id else list(ARTICLES)
    role = args.role
    for article in articles:
        text = {
            "silver_da": article.summary_da,
            "oracle_da": article.oracle_da,
            "lead1_da": article.lead_da,
        }[role]
        book = grade(article, text, role)
        _print(
            f"{article.id}  {role}  {book.passed}/{book.total}  "
            f"fail={list(book.failed) or '-'}"
        )
        if args.id:
            for gate in book.gates:
                mark = "ok" if gate.passed else "FAIL"
                _print(f"  [{mark:4}] {gate.name}: {gate.detail}")
    return 0


def cmd_align(args: argparse.Namespace) -> int:
    article = article_by_id(args.id) if args.id else ARTICLES[0]
    alignment = align_article(article)
    _print(
        f"{article.id} aligned={alignment.aligned} "
        f"pairs={len(alignment.pairs)} quote_i={alignment.quote_index}"
    )
    for pair in alignment.pairs:
        flag = " quote" if pair.is_quote else ""
        _print(
            f"  [{pair.index}] da={pair.da_words}w en={pair.en_words}w "
            f"x{pair.word_ratio:.2f} sub x{pair.subword_ratio:.2f}{flag}"
        )
        _print(f"      DA: {pair.danish}")
        _print(f"      EN: {pair.english}")
    if alignment.leftover_da or alignment.leftover_en:
        _print(f"  leftover_da={list(alignment.leftover_da)}")
        _print(f"  leftover_en={list(alignment.leftover_en)}")
        return 1
    return 0


def cmd_cards(_: argparse.Namespace) -> int:
    written = write_cards()
    for name, path in written.items():
        _print(f"{name}: {path}")
    return 0


def cmd_all(args: argparse.Namespace) -> int:
    cmd_hops(args)
    require_valid(Path(args.out) if args.out else DATA_DIR)
    cmd_report(args)
    cmd_cards(args)
    cmd_notes(args)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sejeroe",
        description="Sejerø Tidende manchet desk — personal, download-free examples.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    hops = sub.add_parser("hops", help="Write course-shaped CSV hops from the fixtures")
    hops.add_argument("--out", default="", help="Output directory (default: examples/data)")
    hops.set_defaults(func=cmd_hops)

    score = sub.add_parser("score", help="Slot, manchet, quote, and overlap scores")
    score.add_argument("--id", default="", help="Article id, for example SEJ-001")
    score.set_defaults(func=cmd_score)

    manchet = sub.add_parser("manchet", help="Score the first sentence as a news lede")
    manchet.add_argument("--id", default="")
    manchet.set_defaults(func=cmd_manchet)

    pack = sub.add_parser("pack", help="Pack a Danish body with course-like budgets")
    pack.add_argument("--id", default="SEJ-001")
    pack.add_argument(
        "--policy",
        default="",
        help="Optional preset: " + ", ".join(sorted(PRESETS)),
    )
    pack.set_defaults(func=cmd_pack)

    length = sub.add_parser("length", help="Danish vs English length inflation")
    length.set_defaults(func=cmd_length)

    walk = sub.add_parser("walk", help="Print every hop for one brief")
    walk.add_argument("--id", default="SEJ-001")
    walk.set_defaults(func=cmd_walk)

    planted = sub.add_parser("planted", help="JSON lines for planted metric blind spots")
    planted.set_defaults(func=cmd_planted)

    report = sub.add_parser("report", help="Write HTML and text desk notes")
    report.set_defaults(func=cmd_report)

    notes = sub.add_parser("notes", help="Print the text desk notes")
    notes.set_defaults(func=cmd_notes)

    validate_cmd = sub.add_parser("validate", help="Validate fixtures and CSV headers")
    validate_cmd.add_argument("--out", default="")
    validate_cmd.set_defaults(func=cmd_validate)

    all_cmd = sub.add_parser("all", help="Write hops, validate, reports, and cards")
    all_cmd.add_argument("--out", default="")
    all_cmd.set_defaults(func=cmd_all)

    baseline = sub.add_parser("baseline", help="Extractive lead-1/lead-2 vs silver vs oracle")
    baseline.add_argument("--id", default="")
    baseline.set_defaults(func=cmd_baseline)

    gates = sub.add_parser("gates", help="Night-editor stylebook gates")
    gates.add_argument("--id", default="")
    gates.add_argument(
        "--role",
        default="silver_da",
        choices=("silver_da", "oracle_da", "lead1_da"),
    )
    gates.set_defaults(func=cmd_gates)

    align = sub.add_parser("align", help="Pair Danish and English sentences")
    align.add_argument("--id", default="SEJ-001")
    align.set_defaults(func=cmd_align)

    cards = sub.add_parser("cards", help="Write per-brief markdown cards")
    cards.set_defaults(func=cmd_cards)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
