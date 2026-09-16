# Troubleshooting

A short list of failures that the 2023 scripts and the new examples
have already seen, or will see the moment you run them on a current
`transformers` / CUDA stack.

## Translation looks like the source language

- You converted only en→da (`Ctranslate_converter.py` as committed)
  and then pointed `translate.py` at a missing `opus-mt-da-en_ct2`.
  CTranslate2 errors are usually loud; a *silent* fallback you invented
  yourself is worse — do not catch that exception and return the source.
- OPUS-MT is being fed NLLB `eng_Latn` / `dan_Latn` prefixes. Remove
  `target_prefix` for Marian/OPUS, or actually convert NLLB.

## `summary.py` finishes in seconds and writes 10 rows

That is the `df[:10]` slice. Delete it for a full run.

## `UnicodeEncodeError` or `Ã¥` in the CSV

Re-export as UTF-8. Do not train. See [dataset.md](dataset.md).

## `LookupError: resource 'punkt' not found`

The GPU scripts call `nltk.download('punkt')` at import time, which
fails on machines without outbound HTTPS or with a filled `/root`.
Download once on a networked box and set `NLTK_DATA`. The examples do
not need NLTK.

## `finetune.py` crashes on `evaluation_strategy`

Recent `transformers` renamed it to `eval_strategy`. Same for
`save_strategy`. Use a `transformers` in the 4.30–4.44 band, or update
the kwargs.

## `datasets.load_metric` is missing

It moved to the `evaluate` package. `eval.py` already imports
`evaluate` but still calls `load_metric`. Prefer `evaluate.load("rouge")`
and `evaluate.load("bertscore")`.

## Eval output is English, or token ids that decode to `<extra_id_0>`

Tokenizer / weight mismatch. `eval.py` builds a tokenizer from
`google/mt5-small` and loads `small_model/`. Those must be the same
size as whatever `finetune.py` wrote.

## CUDA OOM during mT5-large

Drop to `mt5-base` or `mt5-small`, cut `per_device_train_batch_size`,
raise `gradient_accumulation_steps`, shorten encoder `max_length`.
See [training.md](training.md).

## BERTScore hangs on first eval

It is downloading `xlm-roberta-large`. Pre-pull it, or pass a smaller
`model_type` for smoke tests (`bert-base-multilingual-cased` is worse
for Danish but finishes).

## `use_auth_token` TypeError

Deprecated. Use `token=False` or omit the argument.

## Dry-run CSVs do not match `examples/data/`

`examples/output/` is a generated run (and is gitignored).
`examples/data/` is the committed fixture set from
`cli export-data`. Compare the right folder.

## `SchemaError: ... empty values`

A row survived translation but the model returned an empty string.
Drop those ids before fine-tuning; mT5 will happily learn to emit EOS
immediately if empty targets are in the train CSV.

## Examples fail with `ModuleNotFoundError: danish_news_summarization`

Set `PYTHONPATH` to the repository root:

```bash
PYTHONPATH=. python examples/walk_one_article.py
```

or `pip install -e .` once a `pyproject.toml` is added.

## Tests fail on sentence counts

`sent_tokenize` is conservative about abbreviations. If you add a new
abbreviation to a fixture (`bl.a.`, `m.fl.`), add it to
`danish_news_summarization/text.py` `_ABBREVIATIONS` as well, and
extend `tests/test_text.py`.
