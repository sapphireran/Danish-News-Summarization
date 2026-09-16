# Known issues in the December 2023 scripts

I listed only problems I can point at in the current files. This is a personal defect list, not a ticket tracker for a product.

Severity is “how badly it breaks a honest rerun,” not “how embarrassing it is.”

## Blockers (a clean clone will not reproduce training)

### B1. Converter does not build the DA→EN model

`Ctranslate_converter.py` only converts `opus-mt-en-da`. `translate.py` requires `models/opus-mt-da-en_ct2`.

**Fix when rerunning:** uncomment the three `opus_da_en` lines.

### B2. `summary.py` keeps ten rows

```python
df = pd.read_csv(input_file_path)[:10]
```

A full-file rerun is impossible until that slice is removed. I do not know whether the original silver CSVs were built with or without it.

### B3. Fine-tune output name ≠ eval input name

| Script | Path |
| --- | --- |
| `finetune.py` writes | `./large_model` |
| `eval.py` reads | `small_model` |
| `use_model.py` reads | `small_model` |

Also: training uses `google/mt5-large`; eval/use tokenize with `google/mt5-small`.

**Fix when rerunning:** one directory, one tokenizer, saved together.

### B4. Nordjylland column names in `eval.py`

`tokenize_data` reads `input_text` / `target_text`. The public card documents `text` / `summary`. `remove_columns` lists the ScandEval-shaped names. If the loader returns the card schema, `.map` fails.

`use_model.py` uses the mini set and the same ScandEval-shaped names. That may be consistent *for the mini set only*.

### B5. No data in git

Without the 10k CSV and the `datasets/` splits, `translate.py` and `finetune.py` `FileNotFoundError` immediately.

## Silver-label quality risks

### S1. NLLB language prefixes on Marian models

Both translate scripts do:

```python
target_prefixes = [[tgt_lang] for _ in source_tokens]
...
result.hypotheses[0][1:]
```

That is the CTranslate2 NLLB guide. OPUS-MT is bilingual Marian. `eng_Latn` / `dan_Latn` are not Marian language tokens.

Possible effects: a forced unknown token, a wasted first decode step, or a worse hypothesis. The `[1:]` strip assumes a language-code token that may not be there, so the first *real* word can be deleted.

NLLB conversion is commented out; the call site was not fully reverted.

### S2. `src_lang=` on OPUS tokenizers

`AutoTokenizer.from_pretrained(..., src_lang="dan_Latn")` (or `eng_Latn`) is an NLLB/M2M argument. Harmless if ignored; misleading if someone thinks it selected a language pair.

### S3. Back-translation pack budget is 512, not 460

`translate_article(..., tokenizer)` calls `split_into_sentences(article, max_length, tokenizer)` with `max_length=512`. `text_max_length` is computed and unused. Summaries are short, so this is usually latent.

### S4. No overflow split on the way back

`translate_back.py` will pack a too-long sentence as-is. Fine for T5-80 summaries; not a general article translator.

### S5. Map-reduce summaries have no global length cap

A long article becomes many 80-token English summaries concatenated, then Marian Danish, then truncated to 128 tokens at train time. The student never sees a coherent long label; it sees a head.

### S6. Intermediate English is dropped only at the last hop

`summary.py` still writes `translated`. That is useful for debugging. It is also easy to fine-tune on the wrong column if someone edits `finetune.py` carelessly. Current `finetune.py` uses `body` / `summary` from the *back-translated* file, which is correct.

## Evaluation correctness

### E1. Qualitative printer indexes the wrong article

`use_model.py` prints `split_dataset["test"]["input_text"][i]` for dataloader batch `i` with `batch_size=2`. After the first batch, text and generation diverge.

### E2. `no_repeat_ngram_size=1` in the demo script

This is not the trained decoder. Qualitative impressions from 2023 using this script are not impressions of the training generate config.

### E3. `dataloader_drop_last=True` on test

Drops up to 63 examples; 18 on a 4,178-row test with batch 64.

### E4. Deprecated `datasets.load_metric`

Works on old `datasets`, noisy or broken on new ones. Commit `d216a1a` reverted `evaluate.load` back to `load_metric`.

### E5. BERTScore downloaded inside `compute_metrics`

The metric objects are constructed on every evaluate call. Slow, and a Hub failure happens *after* generation. Load once at module level.

### E6. No post-train silver test

`finetune.py` ends at `save_pretrained`. You cannot tell train-set copy from generalization to silver-test without another script.

### E7. Trainer `output_dir` reused as a name

Both train and eval mention `mt5-summarize-large` even when the model is small or eval-only. Easy to load the wrong checkpoint by directory convention.

## Engineering / hygiene

### H1. No CLI, no config, no logging of run IDs

Every path is a literal. Two experiments cannot coexist without copying files.

### H2. No `seed`

Cannot rebuild the same shuffle or the same undocumented CSV split.

### H3. Tokenizer not saved with `large_model`

`save_pretrained` is called on the model only (and on `module` if DataParallel). SentencePiece must be reloaded from the Hub name, and the scripts pick the wrong name.

### H4. Duplicated sentence packing

`translate.py` and `summary.py` each have `split_long_sentence` / `split_into_sentences`. They will drift (they already did: `translate_back.py` is a third, weaker copy).

### H5. Unused imports

`eval.py` imports `os`, `evaluate` (after the revert, `evaluate` is unused), `AutoConfig`. `finetune.py` imports `AutoModelForSeq2SeqLM` twice and `os` only for `makedirs`. Not user-facing.

### H6. `use_auth_token=False`

Old Transformers kwarg. Newer versions want `token=`. Cosmetic until the kwarg is removed.

### H7. `summary.py` still titled “Extract Summary” in the 2023 README

The model is abstractive, not extractive. I keep saying “extract” in old comments out of habit. The method page uses “summarize.”

### H8. No tests

There is no unit test for the packer, no golden sentence for OPUS, no schema test for CSVs. The packer is the one place a 20-line test would have paid rent.

## Things that look like bugs but are intentional

- **`repetition_penalty=5.0`** — extreme but deliberate; see the output filename.
- **`log_level=error`** — I wanted a quiet Trainer; I now think that was a mistake, not a bug.
- **`push_to_hub=False`** — course project, no automatic Hub upload. Good.
- **Silver labels instead of Nordjylland train** — the point of the project, not an accident.
- **Commented NLLB converters** — leftover research branch, useful as history.

## Priority if I touch code later (personal)

Still not this PR.

1. Align checkpoint + tokenizer + columns so `eval.py` can run.
2. Remove `[:10]` and NLLB prefixes.
3. Enable both OPUS conversions.
4. Fix the qualitative index bug.
5. Save a `run.json` next to `large_model`.

Until 1–3 exist, I will not quote a score.
