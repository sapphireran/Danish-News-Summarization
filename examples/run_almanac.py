#!/usr/bin/env python3
"""Rebuild fixtures, run checks, and print the ledger means."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from maalestok.corpus import ARTICLES  # noqa: E402
from maalestok.fixtures import write_all  # noqa: E402
from maalestok.ledger import build_corpus_ledger  # noqa: E402
from maalestok.nllb_scar import demo_cases  # noqa: E402
from maalestok.report import write_report  # noqa: E402
from maalestok.validate import run_checks, summary  # noqa: E402


def main() -> int:
    written = write_all()
    print("fixtures")
    for name, path in written.items():
        print(f"  {name:12} {path}")

    checks = run_checks()
    ok, total = summary(checks)
    print(f"validate {ok}/{total}")
    if ok != total:
        for item in checks:
            if not item.ok:
                print(f"  FAIL {item.name}: {item.detail}")
        return 1

    ledger = build_corpus_ledger(ARTICLES)
    print(
        "means "
        f"pivot={ledger.mean_survival('pivot_en'):.3f} "
        f"summary={ledger.mean_survival('summary_en'):.3f} "
        f"silver={ledger.mean_survival('silver_da'):.3f} "
        f"oracle={ledger.mean_survival('oracle_da'):.3f} "
        f"lead2={ledger.mean_survival('lead2_da'):.3f}"
    )
    worst = ledger.worst()
    print(f"worst {worst.article_id} silver={worst.survival('silver_da'):.3f}")

    print("scar")
    for case in demo_cases():
        flag = "ok" if case.harmless else "DROP"
        print(f"  {flag} {case.name}: dropped {case.dropped!r}")

    html = write_report()
    print(f"report {html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
