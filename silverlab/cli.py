"""Command-line entry for the personal methods lab."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .baselines import run_all_baselines
from .catalog import ERROR_CODES, load_catalog
from .course_csv import write_articles_csv
from .fiction import dump_briefs_json, load_briefs
from .catalog import dump_catalog_json
from .report import write_report
from .rouge import mean_scores, score_pair
from .rubric import score_rubric
from .sentences import split_sentences
from .tables import format_table
from .validate import failed_checks, run_checks
from .fiction import REPO_ROOT


def _cmd_list(_args: argparse.Namespace) -> int:
    briefs = load_briefs()
    rows = []
    for brief in briefs:
        n_sent = len(split_sentences(brief.article_text))
        rows.append((brief.id, brief.topic, str(n_sent), brief.title))
    print(format_table(("id", "topic", "sents", "title"), rows))
    return 0


def _cmd_baselines(args: argparse.Namespace) -> int:
    briefs = load_briefs()
    if args.id:
        briefs = [brief for brief in briefs if brief.id == args.id]
        if not briefs:
            print(f"unknown brief id: {args.id}", file=sys.stderr)
            return 2
    for brief in briefs:
        print(f"\n# {brief.id}  {brief.title}")
        results = run_all_baselines(brief.article_text, brief.title)
        rows = []
        for name, result in results.items():
            rows.append((name, ",".join(str(i) for i in result.sentence_indices), result.summary))
        print(format_table(("baseline", "idx", "summary"), rows))
    return 0


def _cmd_metrics(args: argparse.Namespace) -> int:
    briefs = load_briefs()
    target = args.against
    per_name: dict[str, list[dict[str, float]]] = {}
    detail_rows = []
    for brief in briefs:
        gold = brief.gold_abstractive if target == "abstractive" else brief.gold_extractive
        results = run_all_baselines(brief.article_text, brief.title)
        for name, result in results.items():
            metrics = score_pair(result.summary, gold)
            per_name.setdefault(name, []).append(metrics)
            if args.detail:
                detail_rows.append(
                    (
                        brief.id,
                        name,
                        f"{metrics['rouge1_fmeasure']:.3f}",
                        f"{metrics['rouge2_fmeasure']:.3f}",
                        f"{metrics['rougeL_fmeasure']:.3f}",
                    )
                )
    mean_rows = []
    for name, rows in per_name.items():
        means = mean_scores(rows)
        mean_rows.append(
            (
                name,
                f"{means['rouge1_fmeasure']:.3f}",
                f"{means['rouge2_fmeasure']:.3f}",
                f"{means['rougeL_fmeasure']:.3f}",
            )
        )
    print(f"Mean ROUGE against gold {target} ({len(briefs)} briefs)")
    print(format_table(("baseline", "R1 F", "R2 F", "RL F"), mean_rows))
    if args.detail:
        print()
        print(format_table(("id", "baseline", "R1 F", "R2 F", "RL F"), detail_rows))
    return 0


def _cmd_catalog(_args: argparse.Namespace) -> int:
    items = load_catalog()
    print("Typology")
    print(format_table(("code", "meaning"), list(ERROR_CODES.items())))
    print()
    rows = [
        (
            item.id,
            item.article_id,
            ",".join(item.codes),
            str(item.severity),
            item.explanation,
        )
        for item in items
    ]
    print(format_table(("id", "article", "codes", "sev", "explanation"), rows))
    return 0


def _cmd_rubric(args: argparse.Namespace) -> int:
    briefs = load_briefs()
    if args.id:
        briefs = [brief for brief in briefs if brief.id == args.id]
        if not briefs:
            print(f"unknown brief id: {args.id}", file=sys.stderr)
            return 2
    rows = []
    for brief in briefs:
        lead2 = run_all_baselines(brief.article_text, brief.title)["lead2"].summary
        scores = score_rubric(brief.article_text, lead2, brief.gold_abstractive)
        rows.append(
            (
                brief.id,
                str(scores.faithfulness),
                str(scores.coverage),
                str(scores.fluency),
                str(scores.conciseness),
                str(scores.danish_naturalness),
                f"{scores.mean:.2f}",
                scores.notes,
            )
        )
    print("Heuristic rubric on lead-2 vs gold abstractive")
    print(
        format_table(
            ("id", "faith", "cov", "flu", "conc", "da", "mean", "notes"),
            rows,
        )
    )
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    path = Path(args.out)
    write_report(path)
    print(f"wrote {path}")
    return 0


def _cmd_validate(_args: argparse.Namespace) -> int:
    checks = run_checks()
    failed = failed_checks(checks)
    print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
    if failed:
        for check in failed:
            print(f"FAIL  {check.name}: {check.detail}")
        return 1
    print("corpus and catalog look consistent")
    return 0


def _cmd_export(_args: argparse.Namespace) -> int:
    briefs_path = dump_briefs_json()
    catalog_path = dump_catalog_json()
    csv_path = write_articles_csv()
    print(f"wrote {briefs_path}")
    print(f"wrote {catalog_path}")
    print(f"wrote {csv_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="silverlab",
        description="Personal methods lab for Danish silver-label summarization.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List fictional briefs").set_defaults(func=_cmd_list)

    p_base = sub.add_parser("baselines", help="Run extractive baselines")
    p_base.add_argument("--id", help="Restrict to one lab-* id")
    p_base.set_defaults(func=_cmd_baselines)

    p_metrics = sub.add_parser("metrics", help="Score baselines with from-scratch ROUGE")
    p_metrics.add_argument(
        "--against",
        choices=("abstractive", "extractive"),
        default="abstractive",
        help="Gold column to score against",
    )
    p_metrics.add_argument("--detail", action="store_true", help="Print per-brief rows")
    p_metrics.set_defaults(func=_cmd_metrics)

    sub.add_parser("catalog", help="Print the hop-error catalog").set_defaults(func=_cmd_catalog)

    p_rubric = sub.add_parser("rubric", help="Heuristic five-axis scores on lead-2")
    p_rubric.add_argument("--id", help="Restrict to one lab-* id")
    p_rubric.set_defaults(func=_cmd_rubric)

    p_report = sub.add_parser("report", help="Write the HTML lab report")
    p_report.add_argument(
        "--out",
        default=str(REPO_ROOT / "examples" / "lab_report" / "index.html"),
        help="Destination HTML path",
    )
    p_report.set_defaults(func=_cmd_report)

    sub.add_parser("validate", help="Check corpus and catalog integrity").set_defaults(
        func=_cmd_validate
    )
    sub.add_parser("export-data", help="Rewrite examples/data JSON from the in-module corpus").set_defaults(
        func=_cmd_export
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
