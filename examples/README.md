# Examples

Offline walkthroughs for the 2023 ITU Danish news summarization project. Nothing
in this folder downloads a Hugging Face checkpoint or talks to a GPU. The
original training and translation scripts still live at the repository root.

## What is in `data/`

The fixtures are invented news stories, not scraped articles. They exist so the
CSV schemas and the packing / scoring helpers can be exercised in CI.

| File | Pipeline stage | Columns |
| --- | --- | --- |
| `sample_danish_articles.csv` | raw input to `translate.py` | `id`, `article text` |
| `sample_translated_articles.csv` | output of `translate.py` | `id`, `body`, `translated` |
| `sample_english_summaries.csv` | output of `summary.py` | `id`, `body`, `translated`, `summary` |
| `sample_labeled_danish.csv` | output of `translate_back.py` | `id`, `body`, `summary` |
| `sample_eval_pairs.csv` | qualitative stand-in for `eval.py` | `id`, `input_text`, `target_text`, `prediction` |

Ten stories cover metro construction, climate labs, west-coast fisheries,
property tax, street trees, a Kattegat ferry, a regional hospital, Bornholm
cables, Esbjerg offshore wind, and Aalborg student housing. The English
`translated` / `summary` columns are hand-written parallel text, not model
output. Treat them as schema examples.

## Scripts

Run every command from the repository root so `danish_news_sum` imports cleanly.

```bash
python examples/dry_run_pipeline.py
python examples/chunk_sample_articles.py --max-length 80
python examples/inspect_silver_labels.py
python examples/score_sample_summaries.py
python examples/print_configs.py
```

`dry_run_pipeline.py` loads the four stage CSVs in order, checks columns, and
prints which root script would run next. `chunk_sample_articles.py` shows the
same greedy sentence packing that `translate.py` and `summary.py` use, but with
whitespace tokens instead of SentencePiece. `inspect_silver_labels.py` reports
compression statistics you would want before launching `finetune.py`.
`score_sample_summaries.py` computes ROUGE-like overlap F1 on the committed
prediction / reference pairs. `print_configs.py` dumps the 2023 hyperparameters.

Add `--json` to any of the first four scripts if you want to pipe the report
into another tool.

## Config JSON

`configs/pipeline_defaults.json`, `configs/mt5_large_train.json`, and
`configs/mt5_small_eval.json` restate the constants that are hard-coded in the
root scripts. They are documentation, not a new training CLI. The matching
dataclasses live in `danish_news_sum/config.py`.

## What these examples deliberately skip

- CTranslate2 conversion of OPUS-MT (`Ctranslate_converter.py`)
- Batch translation of a 10k-article dump
- English T5 generation and the back-translation of those summaries
- mT5 fine-tuning and Hugging Face `rouge` / `bertscore`

Those steps need weights, disk, and usually a GPU. See
[docs/reproduction.md](../docs/reproduction.md) if you want to replay the
original experiment.
