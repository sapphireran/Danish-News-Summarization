"""Pack one Danish article into model-sized windows.

This is the CPU counterpart of the sentence packing in `translate.py` and
`summary.py`. It does not load OPUS-MT; it only shows where a 512-token (or
a smaller word) budget would cut the article.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danish_news.chunking import Unit, measure, split_into_windows, split_sentences
from danish_news.config import load_config
from danish_news.reporting import pad_columns
from danish_news.schemas import read_csv
from examples.data.corpus import by_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article-id", default="harbour-plan")
    parser.add_argument("--max-units", type=int, default=None)
    parser.add_argument(
        "--unit",
        choices=("chars", "words", "tokens"),
        default=None,
        help="Override the unit from example_config.json.",
    )
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print windows as JSON instead of a table.",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    max_units = args.max_units if args.max_units is not None else config.max_units
    unit: Unit = args.unit or config.unit  # type: ignore[assignment]

    catalog = by_id()
    if args.article_id not in catalog:
        known = ", ".join(catalog)
        print(f"unknown article id {args.article_id!r}; expected one of: {known}", file=sys.stderr)
        return 2

    article = catalog[args.article_id]
    text = article["article_text"]
    sentences = split_sentences(text)
    windows = split_into_windows(text, max_units, unit)

    print(f"article:     {article['id']} ({article['title']})")
    print(f"characters:  {len(text)}")
    print(f"sentences:   {len(sentences)}")
    print(f"windows:     {len(windows)}  (max_units={max_units} {unit})")
    print(f"source csv:  {config.resolve('raw_csv')}")
    print()

    if args.json:
        payload = [
            {
                "index": index,
                "unit_count": window.unit_count,
                "sentences": list(window.texts),
                "text": window.text,
            }
            for index, window in enumerate(windows)
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    rows = []
    for index, window in enumerate(windows):
        preview = window.text if len(window.text) < 90 else window.text[:87] + "..."
        rows.append(
            {
                "window": index,
                "units": window.unit_count,
                "sents": len(window.texts),
                "preview": preview,
            }
        )
    print(pad_columns(rows, ("window", "units", "sents", "preview")))
    print()
    print("sentence list:")
    for index, sentence in enumerate(sentences):
        print(f"  {index:02d}  ({measure(sentence, unit):3d} {unit})  {sentence}")

    # The raw CSV is the same text; validating it here shows the schema hook.
    rows_on_disk = read_csv(config.resolve("raw_csv"), "raw")
    matching = [row for row in rows_on_disk if row["id"] == args.article_id]
    if matching and matching[0]["article text"] != text:
        print("warning: corpus.py and sample_articles.csv have drifted", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
