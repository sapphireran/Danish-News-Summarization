# Offline examples

These scripts document the 2023 Danish news summarization pipeline **without**
downloading OPUS-MT, T5, mT5, or BERTScore. They use the Python standard
library and the fictional fixtures in [`data/`](data/).

The course scripts in the repo root still expect a GPU workstation. Nothing
here replaces `finetune.py`.

## What to run

From the repository root (stdlib only):

```bash
python examples/run_all.py
```

Or one at a time:

```bash
python examples/test_text_chunking.py
python examples/demo_schema_walkthrough.py
python examples/demo_sentence_chunking.py
python examples/demo_pipeline_dry_run.py
python examples/demo_finetune_preview.py
python examples/demo_offline_metrics.py
```

| Script | What it is for |
| --- | --- |
| `test_text_chunking.py` | Packer / sentence-splitter self-checks |
| `demo_schema_walkthrough.py` | Column names, id joins, UTF-8 `æøå`, train/val/test partition |
| `demo_sentence_chunking.py` | The 2023 sentence packer, including the long `demo-006` sentence |
| `demo_pipeline_dry_run.py` | Stub DA→EN→summary→DA that writes the same CSV names as the course scripts |
| `demo_finetune_preview.py` | Whitespace-token histograms vs the 1024 / 128 truncation caps |
| `demo_offline_metrics.py` | Toy unigram/bigram/LCS F1 on the fake public-eval JSONL |

Shared code:

| Module | Role |
| --- | --- |
| `text_chunking.py` | Packer + the original character-budget long-sentence helper |
| `csv_io.py` | UTF-8 CSV/JSONL without pandas |

## Fixtures

See [`data/README.md`](data/README.md). Six invented Danish news briefs plus
hand-written English pivots and Danish silver summaries. `demo-006` is one
long sentence so the splitter has something to cut.

`demo_pipeline_dry_run.py` writes stub CSVs under `examples/.work/` (gitignored).
Those strings are marked `[en]` and truncated; they are not a substitute for
the hand-written `data/sample_labeled_dataset.csv`.

## Relation to the course scripts

```
Ctranslate_converter.py   — not demoed (needs model download)
translate.py              — packing: demo_sentence_chunking.py
                            wiring:  demo_pipeline_dry_run.py
summary.py                — same, with an explicit --limit (default: no cap)
translate_back.py         — same dry-run, last stage
finetune.py               — preview only (token caps, split sizes)
use_model.py / eval.py    — schema + toy overlap, not Hub datasets
```

If you later plug a real tokenizer into `text_chunking.pack_article`, pass
`tokenizer_len=lambda text: len(hf_tokenizer.encode(text))`. The packer does
not import Transformers itself.

## Why there is no notebook

A notebook that called `Helsinki-NLP/opus-mt-da-en` would re-introduce the
GPU/Hub dependency these examples exist to avoid. The markdown under
[`../docs`](../docs) is the narrative; these scripts are the executable checks.
