# Offline examples

These examples reconstruct the course pipeline's **control flow and
file contracts** without downloading OPUS-MT, T5 or mT5.

Nothing here claims to match the quality of the 2023 silver labels.
Extractive Danish summaries are a floor. Hand-written gold in
`examples/data/` is invented news about fictional towns, used only to
show schemas and overlap metrics.

## Layout

| Path | Role |
| --- | --- |
| `danish_sentences.py` | Abbreviation-aware splitter (no NLTK) |
| `text_chunking.py` | Historical comma-flush packing vs `near_limit` |
| `extractive_summary.py` | TF-IDF-ish sentence picker |
| `schema.py` | Column contracts for every pipeline stage |
| `sample_catalog.py` | Source of truth for the six invented articles |
| `write_sample_csvs.py` | Regenerates `data/*.csv` from the catalog |
| `schema_check.py` | Validates CSVs against `schema.py` |
| `chunking_demo.py` | Prints batches for each sample article |
| `toy_pipeline.py` | Writes stage files + a compression report |
| `compare_summaries.py` | Content-word F1 vs gold |
| `inspect_samples.py` | Inventory of the curated CSVs |
| `configs/*.json` | Hardcoded knobs transcribed from the 2023 scripts |
| `data/` | Committed sample CSVs |

## Commands

From the repository root:

```
python3 examples/schema_check.py --list-schemas
python3 examples/schema_check.py
python3 examples/inspect_samples.py
python3 examples/chunking_demo.py --max-length 40
python3 examples/chunking_demo.py --mode historical --id ex-006-havn
python3 examples/toy_pipeline.py --output-dir examples/output
python3 examples/compare_summaries.py
python3 examples/compare_summaries.py --silver examples/output/labeled_dataset_ml80_rp5.0.csv
```

After editing article text, regenerate the CSVs:

```
python3 examples/write_sample_csvs.py
```

## Tests

```
python3 -m unittest discover -s tests -v
```

The tests cover the splitter, both chunking modes, extractive scoring,
schema failures, catalog row counts, and a temp-dir run of
`toy_pipeline.py`.

## What maps onto the original scripts

| Original | Example stand-in |
| --- | --- |
| `nltk.sent_tokenize` | `split_danish_sentences` |
| `split_long_sentence` + packing | `split_into_sentence_batches` |
| `translate.py` / `translate_back.py` | packing only; no neural MT |
| `summary.py` | `extractive_summarize` |
| `labeled_dataset_ml80_rp5.0.csv` | `data/sample_labeled.csv` (gold) and `output/labeled_dataset_ml80_rp5.0.csv` (silver) |
| ROUGE / BERTScore | `compare_summaries.py` unigram F1 |

Read [docs/pipeline.md](../docs/pipeline.md) for the neural path.
