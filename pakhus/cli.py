"""Command line for the packing-house lab: `python -m pakhus <cmd>`."""

from __future__ import annotations

import argparse
import sys

from pakhus.corpus import ARTICLE_BY_ID, ARTICLES
from pakhus.export import write_lab_data
from pakhus.hops import atlas_for, run_corpus
from pakhus.packing import PACKERS, ascii_atlas, character_vs_token_demo, pack_named
from pakhus.paths import DATA_DIR, REPORT_DIR
from pakhus.report import write_report
from pakhus.scars import scan_repo
from pakhus.sentences import count_false_boundaries, split_danish, split_naive


def _cmd_scars(_args: argparse.Namespace) -> int:
    report = scan_repo()
    sys.stdout.write(report.render())
    return 0 if report.ok else 2


def _cmd_atlas(args: argparse.Namespace) -> int:
    sys.stdout.write(atlas_for(args.article))
    return 0


def _cmd_pack(args: argparse.Namespace) -> int:
    from pakhus.corpus import get_article

    article = get_article(args.article)
    text = article.english if args.packer in {"course_summary", "course_back"} else article.danish
    result = pack_named(args.packer, text)
    sys.stdout.write(ascii_atlas(result, article.id) + "\n")
    if args.packer == "course_translate":
        demo = character_vs_token_demo(article.danish.split(".")[0] + ".", result.budget)
        sys.stdout.write(
            "first-sentence length demo: "
            + ", ".join(f"{k}={v}" for k, v in demo.items())
            + "\n"
        )
    return 0


def _cmd_split(args: argparse.Namespace) -> int:
    from pakhus.corpus import get_article

    article = get_article(args.article)
    naive = split_naive(article.danish)
    danish = split_danish(article.danish)
    counts = count_false_boundaries(article.danish)
    sys.stdout.write(
        f"{article.id}: naive={counts['naive_sentences']} "
        f"danish={counts['danish_sentences']} "
        f"extra_naive_cuts={counts['extra_naive_cuts']}\n"
    )
    sys.stdout.write("\n# danish splitter\n")
    for i, sent in enumerate(danish):
        sys.stdout.write(f"{i:02d}  {sent}\n")
    sys.stdout.write("\n# naive splitter\n")
    for i, sent in enumerate(naive):
        sys.stdout.write(f"{i:02d}  {sent}\n")
    return 0


def _cmd_hops(_args: argparse.Namespace) -> int:
    cascade = run_corpus()
    written = write_lab_data(DATA_DIR, cascade)
    sys.stdout.write(f"wrote {len(written)} files under {DATA_DIR}\n")
    for row in cascade.rows:
        sys.stdout.write(
            f"{row.article.id:8s}  hop1={row.hop1.n_panes}  hop2={row.hop2.n_panes}  "
            f"silver_u={row.concat.silver_units:3d}  "
            f"trunc={int(row.concat.would_truncate_at_128)}  "
            f"p0={row.concat.pane0_share:.2f}  "
            f"surv={row.concat.figure_survival:.2f}\n"
        )
    return 0


def _cmd_report(_args: argparse.Namespace) -> int:
    cascade = run_corpus()
    write_lab_data(DATA_DIR, cascade)
    path = write_report(REPORT_DIR, cascade)
    sys.stdout.write(f"wrote {path}\n")
    return 0


def _cmd_list(_args: argparse.Namespace) -> int:
    for article in ARTICLES:
        sys.stdout.write(
            f"{article.id:8s}  {article.split:10s}  {article.n_sentences:2d} sent  {article.title_da}\n"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pakhus", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("scars", help="scan frozen 2023 scripts").set_defaults(func=_cmd_scars)
    sub.add_parser("list", help="list Toftevig articles").set_defaults(func=_cmd_list)
    sub.add_parser("hops", help="run the CPU cascade and write CSVs").set_defaults(func=_cmd_hops)
    sub.add_parser("report", help="write HTML atlas + CSVs").set_defaults(func=_cmd_report)

    atlas = sub.add_parser("atlas", help="print pane bars for one article")
    atlas.add_argument("--article", required=True, choices=sorted(ARTICLE_BY_ID))
    atlas.set_defaults(func=_cmd_atlas)

    pack = sub.add_parser("pack", help="run one named packer")
    pack.add_argument("--article", required=True, choices=sorted(ARTICLE_BY_ID))
    pack.add_argument("--packer", required=True, choices=sorted(PACKERS))
    pack.set_defaults(func=_cmd_pack)

    split = sub.add_parser("split", help="compare naive vs Danish sentence cuts")
    split.add_argument("--article", required=True, choices=sorted(ARTICLE_BY_ID))
    split.set_defaults(func=_cmd_split)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
