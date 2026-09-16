"""Validate the committed sample CSVs against the pipeline contracts.

    python examples/validate_schemas.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.schemas import (
    PIPELINE_SCHEMAS,
    SAMPLE_FILES,
    describe_schema,
    validate_csv,
)

DATA = ROOT / "examples" / "data"

SPLIT_FILES = {
    "train": "sample_train_split.csv",
    "validation": "sample_validation_split.csv",
    "test": "sample_test_split.csv",
}


def main() -> int:
    print("Pipeline contracts\n")
    for name in (
        "unlabeled_danish",
        "translated",
        "english_summaries",
        "labeled_danish",
        "finetune_split",
        "predictions",
    ):
        print(describe_schema(PIPELINE_SCHEMAS[name]))
        print()

    failures = 0
    print("Sample file checks\n")
    for schema_name, filename in SAMPLE_FILES.items():
        result = validate_csv(DATA / filename, PIPELINE_SCHEMAS[schema_name])
        status = "ok" if result.ok else "FAIL"
        print(f"  [{status}] {filename:32s} rows={result.rows}")
        for error in result.errors:
            print(f"         {error}")
            failures += 1

    split_schema = PIPELINE_SCHEMAS["finetune_split"]
    seen_ids: list[str] = []
    for split, filename in SPLIT_FILES.items():
        result = validate_csv(DATA / filename, split_schema)
        status = "ok" if result.ok else "FAIL"
        print(f"  [{status}] {filename:32s} rows={result.rows} split={split}")
        for error in result.errors:
            print(f"         {error}")
            failures += 1
        if result.ok:
            import csv

            with (DATA / filename).open(encoding="utf-8", newline="") as handle:
                seen_ids.extend(row["id"] for row in csv.DictReader(handle))

    labeled = DATA / "sample_labeled_dataset.csv"
    if labeled.is_file():
        import csv

        with labeled.open(encoding="utf-8", newline="") as handle:
            all_ids = [row["id"] for row in csv.DictReader(handle)]
        if sorted(all_ids) != sorted(seen_ids):
            print("  [FAIL] train/validation/test ids do not partition the labeled set")
            print(f"         labeled={all_ids}")
            print(f"         splits ={seen_ids}")
            failures += 1
        else:
            print("  [ok]  splits partition sample_labeled_dataset.csv")

    if failures:
        print(f"\n{failures} check(s) failed")
        return 1
    print("\nall schema checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
