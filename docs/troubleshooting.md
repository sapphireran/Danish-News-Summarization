# Troubleshooting

Personal recovery notes for the 2023 scripts. Read this before rewriting
half the pipeline.

## Converter ran, `translate.py` still cannot find a model

`Ctranslate_converter.py` only writes `models/opus-mt-en-da_ct2`.
`translate.py` loads `models/opus-mt-da-en_ct2`. Uncomment the da→en
block and convert again.

If the directory exists but is empty or missing `model.bin`, delete it
and reconvert. CTranslate2 does not like a half-written output dir.

## `use_auth_token` TypeError

Newer `transformers` removed `use_auth_token`. Delete the argument or
replace it with `token=None`.

## NLTK `punkt` / `punkt_tab` LookupError

The scripts call `nltk.download('punkt')`. Recent NLTK versions also
need:

```python
nltk.download('punkt_tab')
```

On a machine without outbound network, download once elsewhere and
point `NLTK_DATA` at that tree.

## `summary.py` finished in seconds and only labeled 10 rows

```python
df = pd.read_csv(input_file_path)[:10]
```

Remove the slice. This is the most expensive silent bug in the repo:
everything *looks* successful.

## Fine-tuning crashes on missing `datasets/*.csv`

`translate_back.py` writes `labeled_dataset_ml80_rp5.0.csv`. Nobody
splits it. Create `datasets/` yourself. The dry-run script can emit
example splits from the synthetic labeled file:

```bash
python examples/scripts/split_labeled_dataset.py \
  --input examples/data/sample_labeled.csv \
  --output-dir examples/data/splits
```

## `fp16` / CUDA errors on CPU

`finetune.py` sets `fp16=True`. On CPU this fails. Set `fp16=False`
and, realistically, switch to `google/mt5-small` before trying to train.

## Eval says the model is random after a long training run

Training saves `./large_model`. Eval loads `small_model`. Copy or
repoint. Also confirm the tokenizer size matches the checkpoint
(small vs large).

## `datasets.load_metric` ImportError or deprecation crash

```python
import evaluate
evaluate.load("rouge")
evaluate.load("bertscore")
```

Adapt the key names. The old metric objects exposed `.mid.fmeasure`;
`evaluate` returns floats under `rouge1`, `rouge2`, `rougeL`.

## `alexandrainst/nordjylland-news-summarization` will not download

`eval.py` uses that id; `use_model.py` uses
`ScandEval/nordjylland-news-summarization-mini`. If one Hub id has
moved, try the other, or cache the dataset on a machine with access
and copy the `~/.cache/huggingface/datasets` tree.

Column names must stay `input_text` and `target_text`. If a newer
revision renamed them, add an adapter — do not silently train on the
wrong fields.

## CTranslate2 `Unknown language code` or garbage prefixes

The scripts pass `eng_Latn` / `dan_Latn` as `target_prefix`. OPUS-MT
does not use NLLB language tags. If every output line starts with a
literal tag, stop sending `target_prefixes` and decode
`hypotheses[0]` without the `[1:]` strip.

## Generated Danish summaries start in English

The English T5 summary was passed through the **da→en** model by
mistake, or `translate_back.py` is pointed at the wrong CTranslate2
directory. Check `model_path` and the tokenizer name. They must both
be `en-da` for this stage.

## ROUGE is non-zero but the summaries are English

`eval.py` will still compute ROUGE against Danish references. Character
overlap on numbers and names can fake a small ROUGE-1. Read
`use_model.py` output. If the generation is English, the checkpoint is
wrong or the tokenizer / language prefix is wrong.

## `dataloader_drop_last` makes eval length look suspicious

`eval.py` drops the incomplete last batch. For a test set of 100
examples and batch 64, 36 examples never score. Set
`dataloader_drop_last=False`.

## `use_model.py` article does not match the printed summary

Batch size is 2, but the article is indexed by batch number. Use batch
size 1 when inspecting.

## Pandas `article text` KeyError

The source dump must use that exact column name, including the space.
The synthetic fixture uses the same name. After `translate.py`, the
column is renamed to `body`. Do not feed `translated_articles.csv`
back into `translate.py`.

## Sentence packing produces empty windows

Empty or whitespace-only sentences from `sent_tokenize` can create an
empty `current_list` flush. The examples chunker skips empty sentences.
The 2023 scripts do not. Filter them in pandas first:

```python
df = df[df['article text'].astype(str).str.strip().ne('')]
```

## Out of disk during conversion or training

CTranslate2 conversion and `mt5-summarize-large/` checkpoints are the
two disk hogs. `save_total_limit=1` helps only after the first extra
checkpoint is written. Delete failed `models/*_ct2` dirs by hand.

## Hugging Face Hub rate limits

Every script that calls `from_pretrained` on a Hub id can 429. The
CTranslate2 directories and a local `small_model/` / `large_model/`
avoid Hub access at infer time, but tokenizers still load from Hub in
the committed scripts. After a successful run, the tokenizer files
live in the Hugging Face cache; set `HF_HOME` to a copied cache to
work offline.

## When to stop debugging scripts and use the examples

If you only need to check CSV contracts, column names, or split logic,
do not download OPUS-MT. Run:

```bash
python examples/scripts/dry_run_pipeline.py
python examples/scripts/inspect_dataset.py --stage labeled \
  --path examples/data/sample_labeled.csv
python examples/scripts/compute_overlap_metrics.py \
  --pred examples/data/sample_labeled.csv \
  --gold examples/data/sample_labeled.csv \
  --pred-col summary --gold-col summary
```

The last command is a self-overlap sanity check and should report
perfect scores. If it does not, the metric script is wrong, not the
model.
