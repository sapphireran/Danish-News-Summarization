#!/usr/bin/env python3
"""Show concatenated pane briefs versus the 128-token mT5 label cap."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pakhus.concat import rouge_l
from pakhus.corpus import ARTICLE_BY_ID, get_article
from pakhus.hops import run_article


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", default="tof-001", choices=sorted(ARTICLE_BY_ID))
    args = parser.parse_args()
    article = get_article(args.article)
    row = run_article(article)
    payload = row.concat.as_dict()
    payload["oracle_rouge_l"] = round(rouge_l(row.danish_silver, article.oracle_summary_da), 4)
    payload["n_hop1_panes"] = row.hop1.n_panes
    payload["n_hop2_panes"] = row.hop2.n_panes
    payload["silver_sim_da"] = row.danish_silver
    payload["oracle_da"] = article.oracle_summary_da
    payload["silver_kept_at_128"] = row.concat.silver_kept_at_128
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
