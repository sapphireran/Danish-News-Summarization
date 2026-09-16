# Pipeline

The 2023 project does **not** train a Danish summarizer on human headlines.
It *builds* a Danish dataset by bouncing news through English, then fine-tunes
mT5 on those silver pairs.

```
Danish article
      │
      ▼
 OPUS-MT da→en          translate.py
      │
      ▼
 English T5 summarizer  summary.py
      │
      ▼
 OPUS-MT en→da          translate_back.py
      │
      ▼
 Danish body + Danish silver summary
      │
      ▼
 mT5 fine-tune          finetune.py
      │
      ├─ qualitative peek   use_model.py
      └─ ROUGE / BERTScore  eval.py
```

That detour existed because, in 2023, a strong *Danish* abstractive
checkpoint was harder to come by than a decent English news T5 plus two
OPUS-MT models. The cost is error compounding: a bad translation becomes
a bad English summary becomes a fluent but unfaithful Danish label.

## Stages and artifacts

| Stage | Script | Input | Output | Model |
| --- | --- | --- | --- | --- |
| Convert | `Ctranslate_converter.py` | Helsinki-NLP OPUS-MT | `models/opus-mt-*-ct2` | CTranslate2 |
| Translate | `translate.py` | `10000_articles_without_linebreaks.csv` | `translated_articles.csv` | opus-mt-da-en |
| Summarize | `summary.py` | `translated_articles.csv` | `summarized_file_ml80_rp5.0.csv` | t5-base-finetuned-summarize-news |
| Translate back | `translate_back.py` | the summarized CSV | `labeled_dataset_ml80_rp5.0.csv` | opus-mt-en-da |
| Fine-tune | `finetune.py` | `datasets/{train,validation,test}_dataset.csv` | `./large_model` | google/mt5-large |
| Inspect | `use_model.py` | Nordjylland mini split | stdout | `small_model` |
| Evaluate | `eval.py` | Nordjylland full test | stdout metrics | `small_model` |

The filenames are part of the interface. `summarized_file_ml80_rp5.0.csv`
records the generation settings (`max_length=80`, `repetition_penalty=5.0`)
so two experiments do not silently overwrite each other.

List the same table from code:

```bash
PYTHONPATH=. python -m danish_news_summarization.cli stages
```

## Why articles are chunked

OPUS-MT and the English T5 both sit near a **512-token** context. A
Danish news body is often longer than that, especially after subword
tokenization of compounds (`Universitetshospital`, `miljøkonsekvensvurderingen`).

All three generation scripts therefore:

1. Sentence-split the text (`nltk.sent_tokenize` in the GPU scripts,
   `danish_news_summarization.text.sent_tokenize` in the examples).
2. Split any single sentence that is still over the budget, flushing
   early at `,` / `;` / `:` when possible.
3. Pack consecutive sentences into windows that stay under the budget.
4. Run the model once per window and concatenate the outputs.

`translate.py` uses `text_max_length = int(512 * 0.9)` so a window never
sits exactly on the model limit. `summary.py` packs at 512 and then asks
T5 for a summary of **80** tokens with a heavy repetition penalty.

The shared implementation lives in `danish_news_summarization/chunking.py`.
See [examples.md](examples.md) for a CPU-only walkthrough.

## Column names change on purpose

| Stage | Id | Danish source | English body | Summary language |
| --- | --- | --- | --- | --- |
| raw | `id` | `article text` | — | — |
| translated | `id` | `body` | `translated` | — |
| summarized | `id` | `body` | `translated` | English `summary` |
| labeled / finetune | `id` | `body` | dropped | Danish `summary` |

`translate.py` renames `article text` → `body` and never looks back.
`translate_back.py` drops the English columns so `finetune.py` can treat
`body` / `summary` as a clean seq2seq pair.

Validate a file before spending GPU time:

```bash
PYTHONPATH=. python examples/inspect_schema.py \
  --stage labeled \
  --csv examples/data/sample_labeled_dataset.csv
```

## Things the checked-in scripts do that surprise people

- `Ctranslate_converter.py` converts **only** `opus-mt-en-da`. The da→en
  lines are commented out. Uncomment them before `translate.py`.
- `summary.py` slices `df[:10]`. That is a smoke-test default, not a
  full-corpus run.
- `use_model.py` and `eval.py` score a **public** Nordjylland dataset,
  not the silver labels you just built. That is a feature (out-of-sample)
  but it means you cannot compare those numbers to a training-set ROUGE
  from `finetune.py` without writing it down.
- `eval.py` loads the `google/mt5-small` *tokenizer* and the weights in
  `small_model/`. If those two disagree, generation looks like noise.

## Dry-run stand-in

`examples/dry_run_pipeline.py` walks the same four label-generation
stages on ten fictional articles. It does not call a model. Use it to
learn the schemas and the compression ratios; use the root scripts when
you actually want weights.
