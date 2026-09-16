#!/usr/bin/env python3
"""Offline stand-in for translate → summarize → translate_back.

No models are downloaded. Each stage is a stub so the CSV schemas and
sentence packing can be exercised on a laptop:

* Danish → English: wrap each pack as ``[en] …``
* Summarize: keep the first two sentences of each pack (lede-style)
* English → Danish: unwrap the marker and leave the words (obviously not MT)

The point is the *wiring*, not the words. Real OPUS-MT / T5 output for these
rows lives in ``examples/data/sample_*.csv`` and was written by hand.

    python examples/demo_pipeline_dry_run.py
    python examples/demo_pipeline_dry_run.py --limit 2 --out-dir /tmp/dns-dry
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csv_io import DATA_DIR, read_csv, require_columns, write_csv  # noqa: E402
from text_chunking import pack_article, simple_sent_tokenize  # noqa: E402

EN_MARK = "[en] "


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=DATA_DIR / "sample_source_articles.csv",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / ".work",
        help="Directory for the three stage CSVs (default: examples/.work)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process only the first N rows (0 = all). Mirrors the [:10] "
        "trap in summary.py, except the default here is 'no limit'.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=40,
        help="Whitespace-token pack budget (see demo_sentence_chunking.py)",
    )
    return parser.parse_args()


def stub_translate_da_en(article: str, max_tokens: int) -> str:
    packed = pack_article(article, max_tokens)
    translated_packs = []
    for pack in packed.as_texts():
        # No NLLB language-tag prefix and no hypotheses[0][1:] skip.
        translated_packs.append(EN_MARK + pack)
    return " ".join(translated_packs)


def stub_summarize(english: str, max_words: int = 35) -> str:
    """Lede stub: first sentences, then a hard word cap.

    A single-sentence article (demo-006) has no extra terminals, so a
    sentence-only stub would copy the whole body. The word cap keeps the
    silver row shorter than the article the way a real T5 max_length=80
    decode would.
    """
    unmarked = english.replace(EN_MARK, " ").strip()
    sentences = simple_sent_tokenize(unmarked)
    lede = " ".join(sentences[:2]) if sentences else unmarked
    words = lede.split()
    if len(words) > max_words:
        lede = " ".join(words[:max_words])
    return lede


def stub_translate_en_da(summary_en: str) -> str:
    return summary_en.replace(EN_MARK, "").strip()


def main() -> int:
    args = parse_args()
    rows = read_csv(args.source)
    require_columns(rows, ["id", "article text"], args.source.name)
    if args.limit > 0:
        rows = rows[: args.limit]

    translated_rows = []
    summarized_rows = []
    labeled_rows = []

    for row in rows:
        article_id = row["id"]
        body = row["article text"]
        if not body.strip():
            raise SystemExit(f"{article_id}: empty article text")

        english = stub_translate_da_en(body, args.max_tokens)
        summary_en = stub_summarize(english)
        summary_da = stub_translate_en_da(summary_en)

        if not english.startswith(EN_MARK):
            raise SystemExit(f"{article_id}: stub translator did not mark English")
        if EN_MARK in summary_da:
            raise SystemExit(f"{article_id}: back-translation left the [en] marker")
        if len(summary_da) >= len(body):
            # Stub summaries should be shorter than the article (lede of packs).
            raise SystemExit(f"{article_id}: stub summary is not shorter than the body")

        translated_rows.append({"id": article_id, "body": body, "translated": english})
        summarized_rows.append(
            {
                "id": article_id,
                "body": body,
                "translated": english,
                "summary": summary_en,
            }
        )
        labeled_rows.append({"id": article_id, "body": body, "summary": summary_da})

    out = args.out_dir
    write_csv(out / "translated_articles.csv", translated_rows, ["id", "body", "translated"])
    write_csv(
        out / "summarized_file_ml80_rp5.0.csv",
        summarized_rows,
        ["id", "body", "translated", "summary"],
    )
    write_csv(
        out / "labeled_dataset_ml80_rp5.0.csv",
        labeled_rows,
        ["id", "body", "summary"],
    )

    print(f"Wrote {len(labeled_rows)} silver pairs to {out}")
    print(f"  {out / 'translated_articles.csv'}")
    print(f"  {out / 'summarized_file_ml80_rp5.0.csv'}")
    print(f"  {out / 'labeled_dataset_ml80_rp5.0.csv'}")
    print()
    print("id         body_tok  silver_tok  packs_in_en")
    for row, labeled in zip(rows, labeled_rows):
        body_tok = len(row["article text"].split())
        silver_tok = len(labeled["summary"].split())
        packs = labeled["summary"].count(". ") + (1 if labeled["summary"] else 0)
        print(f"{row['id']:<10} {body_tok:>8}  {silver_tok:>10}  ~{packs}")
    print()
    print("These silver strings are stub output, not OPUS-MT. Compare with")
    print("examples/data/sample_labeled_dataset.csv for hand-written stand-ins.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
