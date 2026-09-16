"""Repository-relative paths used by the desk and the example writers."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
DATA_DIR = EXAMPLES_DIR / "data"
REPORT_DIR = EXAMPLES_DIR / "report"
DOCS_DIR = REPO_ROOT / "docs"
GENERATED_DOCS = DOCS_DIR / "generated"


def ensure_output_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DOCS.mkdir(parents=True, exist_ok=True)
