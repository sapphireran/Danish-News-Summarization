# Script scars (left in place)

The December 2023 files on `main` are the course dump. This branch documents
their defects and does **not** patch them. A later cleanup PR can fix them
one by one; a docs-and-examples branch that silently changes training
behaviour would be a different project.

## Converter only builds one direction

`Ctranslate_converter.py` constructs `Helsinki-NLP/opus-mt-en-da` and writes
`models/opus-mt-en-da_ct2`. The da→en converter is commented out. The README
on `main` still says both models come from that script. `translate.py` wants
`models/opus-mt-da-en_ct2`. A clone that follows the README literally cannot
run step 2.

## NLLB prefixes on OPUS-MT

`translate.py` and `translate_back.py` pass `target_prefix=[[tgt_lang]]`
with `dan_Latn` / `eng_Latn`. Those codes belong to NLLB. OPUS-MT does not
speak them. The converter comments show that NLLB was tried. The prefixes
look like a leftover from that try.

## `summary.py` only keeps ten rows

```python
df = pd.read_csv(input_file_path)[:10]
```

That is a debug slice. It will silently produce a ten-row silver set if
someone reruns the hop.

## Student path disagreement

| Script | Model it names |
| --- | --- |
| `finetune.py` | trains `google/mt5-large`, saves `./large_model` |
| `eval.py` | tokenizer `google/mt5-small`, weights `small_model` |
| `use_model.py` | tokenizer `google/mt5-small`, weights `small_model` |

Either the 2023 run renamed a directory by hand, or eval never pointed at
the checkpoint the trainer wrote.

## Nordjylland column names

`eval.py` loads `alexandrainst/nordjylland-news-summarization` and reads
`input_text` / `target_text`. The official card lists `text` / `summary`.
`use_model.py` loads the ScandEval mini set, which is more likely to use
the harness names. See [nordjylland.md](nordjylland.md).

## Deprecated helpers

- `datasets.load_metric("rouge")` and `load_metric("bertscore")` — moved to
  `evaluate` years ago. `eval.py` already imports `evaluate` and then does
  not use it.
- `use_auth_token=False` on `from_pretrained` — old Transformers API.
- `evaluation_strategy` in `Seq2SeqTrainingArguments` — renamed in later
  Transformers.

## Trainer footnotes

- `fp16 = True` with Adafactor on mT5 is a 2023-era combination I would not
  copy blindly.
- `metric_for_best_model="rouge_1_mid_fmeasure"` requires `compute_metrics`
  to succeed on every eval. A ROUGE install hiccup aborts the run.
- `save_steps = 100` is ignored when `save_strategy="epoch"`.
- `summary.py` hard-codes `repetition_penalty=5.0` and `max_length=80`, then
  writes `summarized_file_ml80_rp5.0.csv`. Those knobs never became CLI flags.

## What I did instead of patching

The lab reimplements sentence splitting, not the CTranslate2 hop. Tests lock
the lab down. The scars stay readable in the original files so a future
patch can point at this note and change one behaviour at a time.
