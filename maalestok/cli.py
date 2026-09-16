"""Command-line entry for the Blåhøj measuring-stick lab."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .budget import compare_budgets
from .corpus import ARTICLES, by_id
from .fixtures import write_all
from .ledger import build_article_ledger, build_corpus_ledger
from .measures import extract_measures
from .nllb_scar import demo_cases
from .packing import pack_article
from .paths import DATA_DIR, GENERATED_DOCS, REPORT_DIR
from .report import write_report
from .validate import run_checks, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="maalestok",
        description="Offline measure-survival lab for the 2023 silver-label hops.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list the sixteen almanac briefs")

    p_show = sub.add_parser("show", help="print one brief and its measures")
    p_show.add_argument("article_id")

    p_pack = sub.add_parser("pack", help="pack one brief with the 2023 windows")
    p_pack.add_argument("article_id")
    p_pack.add_argument("--budget", type=int, default=80)

    p_ledger = sub.add_parser("ledger", help="print survival table")
    p_ledger.add_argument("--article", dest="article_id")

    sub.add_parser("scar", help="show the NLLB-prefix decode cases")
    sub.add_parser("validate", help="run closed-world checks")
    sub.add_parser("fixtures", help="rewrite example CSVs")

    p_report = sub.add_parser("report", help="write the HTML almanac")
    p_report.add_argument("--out", type=Path)

    p_budget = sub.add_parser("budget", help="compare char+1 vs approx tokens")
    p_budget.add_argument("article_id")
    p_budget.add_argument("--budget", type=int, default=80)

    args = parser.parse_args(argv)
    handlers = {
        "list": _cmd_list,
        "show": _cmd_show,
        "pack": _cmd_pack,
        "ledger": _cmd_ledger,
        "scar": _cmd_scar,
        "validate": _cmd_validate,
        "fixtures": _cmd_fixtures,
        "report": _cmd_report,
        "budget": _cmd_budget,
    }
    return handlers[args.cmd](args)


def _cmd_list(_: argparse.Namespace) -> int:
    for article in ARTICLES:
        planted = ",".join(err.code for err in article.planted)
        print(f"{article.id}\t{article.topic}\t{article.title}\t{planted}")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    article = by_id(args.article_id)
    print(f"# {article.id} {article.title}")
    print(article.body_da)
    print("\n## source measures")
    for measure in extract_measures(article.body_da):
        kind, value, unit = measure.normalized()
        print(f"- {measure.raw!r:24} {kind:12} {value} {unit}")
    print("\n## silver")
    print(article.silver_da)
    print("\n## planted")
    for err in article.planted:
        print(f"- {err.code}: {err.source_raw} → {err.silver_raw}")
    return 0


def _cmd_pack(args: argparse.Namespace) -> int:
    article = by_id(args.article_id)
    windows = pack_article(article.body_da, budget=args.budget)
    for window in windows:
        flag = " flush" if window.flushed_on_punct else ""
        print(
            f"[{window.index}] tok≈{window.approx_tokens} char+1={window.char_plus_one}{flag}"
        )
        print(f"    {window.text}")
    return 0


def _cmd_ledger(args: argparse.Namespace) -> int:
    if args.article_id:
        article = by_id(args.article_id)
        entry = build_article_ledger(article)
        print(f"{entry.article_id} source={entry.source_count}")
        for hop, pairs in entry.pairs.items():
            print(f"  {hop:12} survival={entry.survival(hop):.2f}")
            for pair in pairs:
                if pair.label == "ok":
                    continue
                target = pair.target.raw if pair.target is not None else "—"
                print(f"    {pair.label:16} {pair.source.raw} → {target} ({pair.detail})")
        return 0

    ledger = build_corpus_ledger(ARTICLES)
    print("id\tsilver\toracle\tlead2\tpivot\tsummary")
    for entry in ledger.articles:
        print(
            f"{entry.article_id}\t{entry.survival('silver_da'):.2f}\t"
            f"{entry.survival('oracle_da'):.2f}\t{entry.survival('lead2_da'):.2f}\t"
            f"{entry.survival('pivot_en'):.2f}\t{entry.survival('summary_en'):.2f}"
        )
    print(
        f"mean\t{ledger.mean_survival('silver_da'):.2f}\t"
        f"{ledger.mean_survival('oracle_da'):.2f}\t"
        f"{ledger.mean_survival('lead2_da'):.2f}\t"
        f"{ledger.mean_survival('pivot_en'):.2f}\t"
        f"{ledger.mean_survival('summary_en'):.2f}"
    )
    worst = ledger.worst()
    print(f"worst_silver\t{worst.article_id}\t{worst.survival('silver_da'):.2f}")
    return 0


def _cmd_scar(_: argparse.Namespace) -> int:
    payload = [
        {
            "name": case.name,
            "hypothesis": list(case.hypothesis),
            "decoded": list(case.decoded),
            "dropped": case.dropped,
            "harmless": case.harmless,
            "note": case.note,
        }
        for case in demo_cases()
    ]
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cmd_validate(_: argparse.Namespace) -> int:
    checks = run_checks()
    ok, total = summary(checks)
    for item in checks:
        mark = "ok" if item.ok else "FAIL"
        if not item.ok:
            print(f"{mark}\t{item.name}\t{item.detail}")
    print(f"{ok}/{total} checks passed")
    return 0 if ok == total else 1


def _cmd_fixtures(_: argparse.Namespace) -> int:
    written = write_all()
    for name, path in written.items():
        print(f"{name}\t{path}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    path = write_report(args.out)
    snapshot = GENERATED_DOCS / "almanac-ledger.txt"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    ledger = build_corpus_ledger(ARTICLES)
    lines = [
        "Blåhøj Almanak ledger",
        f"mean silver={ledger.mean_survival('silver_da'):.3f}",
        f"mean oracle={ledger.mean_survival('oracle_da'):.3f}",
        f"mean lead2={ledger.mean_survival('lead2_da'):.3f}",
        f"html={path}",
    ]
    snapshot.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(path)
    print(snapshot)
    if path.resolve() != (REPORT_DIR / "index.html").resolve() and args.out:
        pass
    return 0


def _cmd_budget(args: argparse.Namespace) -> int:
    article = by_id(args.article_id)
    for row in compare_budgets(article, budget=args.budget):
        print(
            f"[{row.index}] char+1={row.char_plus_one} tok≈{row.approx_tokens} "
            f"ratio={row.ratio:.2f} {row.preview}"
        )
    return 0
