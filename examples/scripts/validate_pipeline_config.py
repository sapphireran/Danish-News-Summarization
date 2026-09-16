#!/usr/bin/env python3
"""Parse the example JSON configs and check they still name real files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from text_lib import CONFIG_DIR, REPO_ROOT


REQUIRED_PIPELINE_STAGES = (
    "convert",
    "translate_da_en",
    "summarize_en",
    "translate_en_da",
    "split",
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def check_exists(relpath: str) -> bool:
    if not relpath:
        return False
    return (REPO_ROOT / relpath).is_file()


def validate_pipeline(config: dict) -> list[str]:
    errors: list[str] = []
    stages = config.get("stages") or {}
    for name in REQUIRED_PIPELINE_STAGES:
        if name not in stages:
            errors.append(f"pipeline: missing stage {name!r}")
            continue
        script = stages[name].get("script")
        if not script:
            errors.append(f"pipeline.{name}: no script")
            continue
        # Root 2023 scripts should exist; example scripts too.
        if not check_exists(script):
            errors.append(f"pipeline.{name}: script {script!r} is not in the repo")
    convert = stages.get("convert") or {}
    models = convert.get("models") or {}
    if "da_en" not in models or "en_da" not in models:
        errors.append("pipeline.convert: need da_en and en_da model blocks")
    elif models["da_en"].get("enabled_in_2023_script") is not False:
        errors.append(
            "pipeline.convert.da_en: 2023 script leaves this commented out; "
            "the example config should record enabled_in_2023_script=false"
        )
    summarize = stages.get("summarize_en") or {}
    if summarize.get("debug_row_limit") != 10:
        errors.append("pipeline.summarize_en: debug_row_limit should record the 2023 [:10] slice")
    return errors


def validate_finetune(config: dict) -> list[str]:
    errors: list[str] = []
    if config.get("model_name") != "google/mt5-large":
        errors.append("finetune: model_name should record google/mt5-large")
    training = config.get("training") or {}
    if training.get("fp16") is not True:
        errors.append("finetune: fp16 should record the 2023 True (and the CPU warning lives in notes)")
    if config.get("eval_scripts_expect") != "small_model":
        errors.append("finetune: eval_scripts_expect should record small_model")
    if config.get("final_save_dir") != "large_model":
        errors.append("finetune: final_save_dir should record large_model")
    data = config.get("data") or {}
    for key in ("train", "validation", "test"):
        if key not in data:
            errors.append(f"finetune.data: missing {key}")
    return errors


def validate_evaluation(config: dict) -> list[str]:
    errors: list[str] = []
    qualitative = config.get("qualitative") or {}
    quantitative = config.get("quantitative") or {}
    if qualitative.get("dataset") == quantitative.get("dataset"):
        errors.append("evaluation: the two 2023 scripts should record *different* dataset ids")
    if not qualitative.get("known_issues"):
        errors.append("evaluation.qualitative: record the known issues")
    if quantitative.get("dataloader_drop_last") is not True:
        errors.append("evaluation.quantitative: dataloader_drop_last should record True")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="Validate a single pipeline JSON")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate every example JSON in examples/configs/",
    )
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.config and not args.all:
        args.all = True

    jobs: list[tuple[str, Path, callable]] = []
    if args.config:
        jobs.append(("pipeline", Path(args.config), validate_pipeline))
    if args.all:
        jobs = [
            ("pipeline", CONFIG_DIR / "pipeline.example.json", validate_pipeline),
            ("finetune", CONFIG_DIR / "finetune.example.json", validate_finetune),
            ("evaluation", CONFIG_DIR / "evaluation.example.json", validate_evaluation),
        ]

    report = []
    failures = 0
    for kind, path, validator in jobs:
        if not path.is_file():
            report.append({"kind": kind, "path": str(path), "errors": [f"missing {path}"], "ok": False})
            failures += 1
            continue
        config = load_json(path)
        errors = validator(config)
        ok = not errors
        if not ok:
            failures += 1
        report.append({"kind": kind, "path": str(path), "errors": errors, "ok": ok})

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for item in report:
            status = "ok" if item["ok"] else "FAIL"
            print(f"[{status}] {item['kind']}: {item['path']}")
            for error in item["errors"]:
                print(f"  - {error}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
