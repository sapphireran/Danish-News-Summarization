from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
DOCS_DIR = REPO_ROOT / "docs"
EXAMPLES_DIR = REPO_ROOT / "examples"
DATA_DIR = EXAMPLES_DIR / "data"
REPORT_DIR = EXAMPLES_DIR / "report"
GENERATED_DOCS = DOCS_DIR / "generated"
