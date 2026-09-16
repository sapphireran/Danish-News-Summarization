"""Write Toftevig CSVs that match the 2023 hop contracts."""

from __future__ import annotations

from pathlib import Path

from pakhus.csvio import write_dicts
from pakhus.hops import (
    Cascade,
    concat_rows,
    finetune_rows,
    hop0_rows,
    hop1_rows,
    hop2_rows,
    hop3_rows,
    oracle_rows,
    pane_trace_rows,
    public_eval_rows,
    run_corpus,
)
from pakhus.paths import DATA_DIR
from pakhus.schemas import HOP0_RAW, HOP1_TRANSLATED, HOP2_SUMMARIZED, HOP3_LABELED, HOP4_FINETUNE, LAB_FILENAMES, PANE_TRACE, PUBLIC_EVAL, validate_table


def write_lab_data(directory: Path | None = None, cascade: Cascade | None = None) -> dict[str, Path]:
    directory = directory or DATA_DIR
    directory.mkdir(parents=True, exist_ok=True)
    cascade = cascade or run_corpus()
    mapping: dict[str, tuple[list[dict[str, object]], tuple[str, ...] | None]] = {
        "hop0_raw": (hop0_rows(cascade), HOP0_RAW.columns),
        "hop1_translated": (hop1_rows(cascade), HOP1_TRANSLATED.columns),
        "hop2_summarized": (hop2_rows(cascade), HOP2_SUMMARIZED.columns),
        "hop3_labeled": (hop3_rows(cascade), HOP3_LABELED.columns),
        "hop3_oracle": (oracle_rows(cascade), HOP3_LABELED.columns),
        "hop4_train": (finetune_rows(cascade, "train"), HOP4_FINETUNE.columns),
        "hop4_validation": (finetune_rows(cascade, "validation"), HOP4_FINETUNE.columns),
        "hop4_test": (finetune_rows(cascade, "test"), HOP4_FINETUNE.columns),
        "public_eval": (public_eval_rows(cascade), PUBLIC_EVAL.columns),
        "pane_trace": (pane_trace_rows(cascade), PANE_TRACE.columns),
        "concat_scores": (concat_rows(cascade), None),
    }
    written: dict[str, Path] = {}
    problems: list[str] = []
    contract_for = {
        "hop0_raw": HOP0_RAW,
        "hop1_translated": HOP1_TRANSLATED,
        "hop2_summarized": HOP2_SUMMARIZED,
        "hop3_labeled": HOP3_LABELED,
        "hop3_oracle": HOP3_LABELED,
        "hop4_train": HOP4_FINETUNE,
        "hop4_validation": HOP4_FINETUNE,
        "hop4_test": HOP4_FINETUNE,
        "public_eval": PUBLIC_EVAL,
        "pane_trace": PANE_TRACE,
    }
    for key, (rows, fields) in mapping.items():
        path = directory / LAB_FILENAMES[key]
        write_dicts(path, rows, fieldnames=fields)
        written[key] = path
        if key in contract_for:
            problems.extend(validate_table(contract_for[key], rows))
    if problems:
        raise ValueError("lab CSV failed contracts:\n" + "\n".join(problems[:20]))
    return written
