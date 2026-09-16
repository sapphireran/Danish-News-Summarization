#!/usr/bin/env python3
"""Validate lab CSVs against the 2023 column contracts."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pakhus.csvio import read_dicts
from pakhus.export import write_lab_data
from pakhus.paths import DATA_DIR
from pakhus.schemas import (
    HOP0_RAW,
    HOP1_TRANSLATED,
    HOP2_SUMMARIZED,
    HOP3_LABELED,
    HOP4_FINETUNE,
    LAB_FILENAMES,
    PUBLIC_EVAL,
    SchemaError,
    assert_article_text_column,
    validate_table,
)


def main() -> int:
    if not (DATA_DIR / LAB_FILENAMES["hop0_raw"]).is_file():
        write_lab_data(DATA_DIR)
    checks = [
        ("hop0_raw", HOP0_RAW),
        ("hop1_translated", HOP1_TRANSLATED),
        ("hop2_summarized", HOP2_SUMMARIZED),
        ("hop3_labeled", HOP3_LABELED),
        ("hop3_oracle", HOP3_LABELED),
        ("hop4_train", HOP4_FINETUNE),
        ("public_eval", PUBLIC_EVAL),
    ]
    problems: list[str] = []
    for key, contract in checks:
        path = DATA_DIR / LAB_FILENAMES[key]
        rows = read_dicts(path)
        problems.extend(validate_table(contract, rows))
        if key == "hop0_raw":
            try:
                assert_article_text_column(list(rows[0].keys()))
            except SchemaError as exc:
                problems.append(str(exc))
    if problems:
        sys.stderr.write("contract failures:\n")
        for item in problems:
            sys.stderr.write(f"  {item}\n")
        return 1
    sys.stdout.write(f"ok  {len(checks)} contracts under {DATA_DIR}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
