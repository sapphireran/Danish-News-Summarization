"""Command-line workbook for the personal Kystlinje archive."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .align import lost_entities, render_alignment, surviving_entities
from .corpus import all_briefs, brief_by_id
from .exercises import grade, questions
from .ledger import HOPS, build_all_ledgers, build_ledger, hop_loss_table, mean_survival
from .pack import pack_article
from .report import write_report
from .schemas import COURSE_SCHEMAS
from .tables import write_all_tables
from .validate import run_checks, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="kystlinje",
        description="Personal, download-free workbook for the 2023 Danish summarization project.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List the 18 fictional briefs")
    show = sub.add_parser("show", help="Print every hop for one brief")
    show.add_argument("id")

    led = sub.add_parser("ledger", help="Entity-survival table")
    led.add_argument("--id", dest="brief_id")

    al = sub.add_parser("align", help="Bracket source tokens that survive into a hop")
    al.add_argument("id")
    al.add_argument("--hop", default="silver", choices=[h for h in HOPS if h != "source"])

    pk = sub.add_parser("pack", help="Pack one brief with the 2023 character-budget splitter")
    pk.add_argument("id")
    pk.add_argument("--budget", type=int, default=80)
    pk.add_argument("--unit", choices=("char", "token"), default="char")

    sub.add_parser("schemas", help="Print the 2023 CSV contracts")

    quiz = sub.add_parser("quiz", help="Print workbook questions")
    quiz.add_argument("--answers", action="store_true")
    quiz.add_argument("--grade", nargs=2, metavar=("N", "ATTEMPT"))

    val = sub.add_parser("validate", help="Run corpus and ledger self-checks")
    val.add_argument("--quiet", action="store_true")

    tables = sub.add_parser("write-tables", help="Write course-shaped CSVs into examples/data")
    tables.add_argument("--out", type=Path)

    rep = sub.add_parser("report", help="Write the HTML entity-telescope notebook")
    rep.add_argument("--out", type=Path)

    args = parser.parse_args(argv)
    handlers = {
        "list": _cmd_list,
        "show": _cmd_show,
        "ledger": _cmd_ledger,
        "align": _cmd_align,
        "pack": _cmd_pack,
        "schemas": _cmd_schemas,
        "quiz": _cmd_quiz,
        "validate": _cmd_validate,
        "write-tables": _cmd_tables,
        "report": _cmd_report,
    }
    return handlers[args.cmd](args)


def _cmd_list(_: argparse.Namespace) -> int:
    for brief in all_briefs():
        print(f"{brief.id}  {brief.title_da}")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    brief = brief_by_id(args.id)
    print(f"# {brief.id} — {brief.title_da}")
    print(f"# {brief.title_en}")
    print()
    print("## Danish source")
    print(brief.body_da)
    print()
    print("## English pivot")
    print(brief.pivot_en)
    print()
    print("## English summary")
    print(brief.summary_en)
    print()
    print("## Danish silver")
    print(brief.silver_da)
    print()
    print("## Lead-2")
    print(brief.lead2_da)
    print()
    print("## Planted scars")
    for err in brief.planted:
        print(f"- {err.code} @{err.hop}: {err.source_span!r} → {err.drifted_span!r}")
        print(f"  {err.note}")
    return 0


def _cmd_ledger(args: argparse.Namespace) -> int:
    if args.brief_id:
        ledgers = [build_ledger(brief_by_id(args.brief_id))]
    else:
        ledgers = build_all_ledgers()
        print("mean survival  pivot={:.3f}  summary={:.3f}  silver={:.3f}  lead2={:.3f}".format(
            mean_survival(ledgers, "pivot"),
            mean_survival(ledgers, "summary"),
            mean_survival(ledgers, "silver"),
            mean_survival(ledgers, "lead2"),
        ))
        print("mean lost     " + "  ".join(f"{a}->{b}={n:.2f}" for a, b, n in hop_loss_table(ledgers)))
        print()
    header = f"{'id':6} {'kind':10} {'surface':28} " + " ".join(f"{h:8}" for h in HOPS)
    print(header)
    print("-" * len(header))
    for led in ledgers:
        for row in led.rows:
            flags = " ".join(f"{'yes':8}" if row.survived(h) else f"{'no':8}" for h in HOPS)
            print(f"{led.brief.id:6} {row.entity.kind:10} {row.entity.surface[:28]:28} {flags}")
        if args.brief_id:
            print()
            print("kept in silver:", ", ".join(e.surface for e in surviving_entities(led, "silver")) or "—")
            print("lost in silver:", ", ".join(e.surface for e in lost_entities(led, "silver")) or "—")
    return 0


def _cmd_align(args: argparse.Namespace) -> int:
    brief = brief_by_id(args.id)
    print(render_alignment(brief, hop=args.hop))
    return 0


def _cmd_pack(args: argparse.Namespace) -> int:
    brief = brief_by_id(args.id)
    windows = pack_article(brief.body_da, budget=args.budget, unit=args.unit)
    print(f"{brief.id}  budget={args.budget}  unit={args.unit}  windows={len(windows)}")
    for win in windows:
        print(f"  [{win.index}] chars={win.char_len} tokens={win.token_len}  {win.text}")
    return 0


def _cmd_schemas(_: argparse.Namespace) -> int:
    for schema in COURSE_SCHEMAS:
        print(f"{schema.name:16}  {schema.script}")
        print(f"  columns: {', '.join(schema.columns)}")
        print(f"  {schema.notes}")
        print()
    return 0


def _cmd_quiz(args: argparse.Namespace) -> int:
    if args.grade:
        number, attempt = int(args.grade[0]), args.grade[1]
        ok, expected = grade(number, attempt)
        print("ok" if ok else f"wrong (expected {expected})")
        return 0 if ok else 1
    for q in questions():
        print(f"{q.number}. {q.prompt}")
        if args.answers:
            print(f"   → {q.answer}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    checks = run_checks()
    ok, total = summary(checks)
    if not args.quiet:
        for check in checks:
            mark = "PASS" if check.ok else "FAIL"
            print(f"{mark:4}  {check.name}: {check.detail}")
    print(f"{ok}/{total} checks passed")
    return 0 if ok == total else 1


def _cmd_tables(args: argparse.Namespace) -> int:
    paths = write_all_tables(args.out)
    for path in paths:
        print(path)
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    path = write_report(args.out)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
