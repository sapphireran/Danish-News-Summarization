"""Score silver Danish labels against independent reference headlines.

`eval.py` uses Hugging Face `rouge` and BERTScore on Nordjylland gold data.
This example uses the dependency-free scorer in `danish_news.scoring` on the
eight fixture articles so the metric definitions are visible without a GPU.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news.config import load_config
from danish_news.reporting import markdown_table, pad_columns
from danish_news.schemas import read_csv
from danish_news.scoring import mean_reports, score_pair


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument(
        "--format",
        choices=("table", "markdown", "json"),
        default="table",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    labeled = {row["id"]: row for row in read_csv(config.resolve("labeled_csv"), "labeled")}
    references = {
        row["id"]: row for row in read_csv(config.resolve("references_csv"), "labeled")
    }
    missing = sorted(set(labeled) ^ set(references))
    if missing:
        print(f"id mismatch between labeled and reference CSVs: {missing}", file=sys.stderr)
        return 1

    reports = []
    rows = []
    for article_id in labeled:
        report = score_pair(
            prediction=labeled[article_id]["summary"],
            reference=references[article_id]["summary"],
            source=labeled[article_id]["body"],
        )
        reports.append(report)
        payload = report.as_dict()
        payload["id"] = article_id
        rows.append(payload)

    averages = mean_reports(reports)
    columns = (
        "id",
        "rouge1_f1",
        "rouge2_f1",
        "rougeL_f1",
        "compression",
        "novelty_unigram",
        "pred_tokens",
        "ref_tokens",
    )

    if args.format == "json":
        print(json.dumps({"rows": rows, "mean": averages}, ensure_ascii=False, indent=2))
        return 0

    renderer = markdown_table if args.format == "markdown" else pad_columns
    print(renderer(rows, columns))
    print()
    print("corpus mean")
    mean_row = [{"id": "mean", **averages}]
    print(renderer(mean_row, columns))
    print()
    print(
        "These F1 numbers are overlap with a second human headline, not Nordjylland "
        "ROUGE from eval.py. Compression is summary tokens / article tokens."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
