"""Run the four pipeline stages with a glossary backend, not OPUS-MT.

The original GPU scripts write `translated_articles.csv`, then
`summarized_file_ml80_rp5.0.csv`, then `labeled_dataset_ml80_rp5.0.csv`.
This dry-run does the same handoff on the eight fixture articles and writes
the stage files under `examples/output/` so the hand-authored fixtures in
`examples/data/` are not overwritten.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news.config import load_config
from danish_news.glossary import GlossaryBackend
from danish_news.pipeline import labeled_rows, run_pivot, summarized_rows, translated_rows
from danish_news.reporting import pad_columns
from danish_news.schemas import read_csv, write_csv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "examples" / "output",
        help="Where to write the dry-run stage CSVs.",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    raw_rows = read_csv(config.resolve("raw_csv"), "raw")
    backend = GlossaryBackend()
    records = run_pivot(raw_rows, backend, config.pipeline())

    args.output_dir.mkdir(parents=True, exist_ok=True)
    written = {
        "translated": write_csv(
            args.output_dir / "translated_articles.csv",
            translated_rows(records),
            "translated",
        ),
        "summarized_en": write_csv(
            args.output_dir / "summarized_file_ml80_rp5.0.csv",
            summarized_rows(records),
            "summarized_en",
        ),
        "labeled": write_csv(
            args.output_dir / "labeled_dataset_ml80_rp5.0.csv",
            labeled_rows(records),
            "labeled",
        ),
    }

    table = []
    for record in records:
        table.append(
            {
                "id": record.id,
                "windows": len(record.windows),
                "da": len(record.body.split()),
                "en": len(record.translated.split()),
                "sum_en": len(record.summary_en.split()),
                "sum_da": len(record.summary.split()),
            }
        )
    print(f"backend:  GlossaryBackend (not OPUS-MT)")
    print(f"raw csv:  {config.resolve('raw_csv')}")
    print(f"windows:  max_units={config.max_units} {config.unit}")
    print()
    print(pad_columns(table, ("id", "windows", "da", "en", "sum_en", "sum_da")))
    print()
    for stage, path in written.items():
        print(f"wrote {stage:16s} {path}")

    print()
    print("sample silver label (harbour-plan):")
    harbour = next(record for record in records if record.id == "harbour-plan")
    print(f"  DA body   : {harbour.body[:160]}...")
    print(f"  EN pivot  : {harbour.translated[:160]}...")
    print(f"  EN summary: {harbour.summary_en}")
    print(f"  DA label  : {harbour.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
