#!/usr/bin/env bash
# Run the offline example suite from the repository root.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "error: python3 or python is required" >&2
  exit 127
fi

"$PYTHON" examples/write_sample_csvs.py
"$PYTHON" examples/schema_check.py
"$PYTHON" examples/inspect_samples.py
"$PYTHON" examples/chunking_demo.py --max-length 40
"$PYTHON" examples/toy_pipeline.py --output-dir examples/output
"$PYTHON" examples/compare_summaries.py
"$PYTHON" examples/compare_summaries.py --silver examples/output/labeled_dataset_ml80_rp5.0.csv
"$PYTHON" -m unittest discover -s tests -v
