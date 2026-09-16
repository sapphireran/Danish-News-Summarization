"""Paths relative to the repository root (parent of the `pakhus` package)."""

from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
DOCS_DIR = REPO_ROOT / "docs"
EXAMPLES_DIR = REPO_ROOT / "examples"
DATA_DIR = EXAMPLES_DIR / "data"
REPORT_DIR = EXAMPLES_DIR / "report"
EXPECTED_DIR = EXAMPLES_DIR / "expected_outputs"
TESTS_DIR = REPO_ROOT / "tests"

COURSE_SCRIPTS = (
    "Ctranslate_converter.py",
    "translate.py",
    "summary.py",
    "translate_back.py",
    "finetune.py",
    "use_model.py",
    "eval.py",
)


def course_script(name: str) -> Path:
    if name not in COURSE_SCRIPTS:
        raise FileNotFoundError(f"not a frozen 2023 script: {name}")
    path = REPO_ROOT / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return path
