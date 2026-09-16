# Pipeline, file by file

This page is a walking tour of the December 2023 scripts. I wrote it by reading the files in `/workspace` in September 2026, not by re-running the GPU jobs.

## 0. Shared habits

Almost every script:

- downloads `nltk` `punkt` on import if it is missing
- picks `cuda` when `torch.cuda.is_available()` else `cpu`
- hard-codes input and output CSV names in the module body
- assumes UTF-8 pandas I/O
- does not use a CLI (`argparse` is absent)

There is no shared library. Sentence packing was copy-pasted between `translate.py` and `summary.py`. `translate_back.py` has a simpler splitter that does **not** break oversized sentences on punctuation.

## 1. `Ctranslate_converter.py`

**Purpose:** turn a Transformers Marian checkpoint into a CTranslate2 directory so batch translation is faster than raw Hugging Face generate.

**Active code (as committed):**

```python
opus_en_da_model = TransformersConverter("Helsinki-NLP/opus-mt-en-da")
output_dir_opus_en_da = "models/opus-mt-en-da_ct2"
opus_en_da_model.convert(output_dir_opus_en_da)
```

**Commented experiments:**

- `facebook/nllb-200-3.3B` → `models/nllb-200-3.3B_ct2`
- `facebook/nllb-200-distilled-600m` → `models/nllb-200-distilled-600m_ct2`
- `Helsinki-NLP/opus-mt-da-en` → `models/opus-mt-da-en_ct2`

`translate.py` loads `models/opus-mt-da-en_ct2`. That conversion is commented out, so a clean clone plus `python Ctranslate_converter.py` is not enough for step 2. I treated the converter as a scratch pad while deciding NLLB vs OPUS, then shipped the last edit.

CTranslate2 conversion is one-way in this repo: there is no script that checks BLEU on a held-out DA↔EN sample after conversion.

## 2. `translate.py` — Danish to English

| Item | Value |
| --- | --- |
| Input | `10000_articles_without_linebreaks.csv` |
| Required columns | `article text`, `id` |
| Model dir | `models/opus-mt-da-en_ct2` |
| Tokenizer | `Helsinki-NLP/opus-mt-da-en` |
| Output | `translated_articles.csv` (`id`, `body`, `translated`) |
| Max length | 512 tokens; packing budget `int(512 * 0.9)` = 460 |

### How an article is split

1. `nltk.sent_tokenize` on the raw Danish body.
2. Each sentence is measured with the Marian tokenizer, `add_special_tokens=True`.
3. Sentences longer than 460 tokens go through `split_long_sentence`: walk words, break on `,` / `;` / `:` when under the budget, otherwise hard-break.
4. Sentences (or chunks) are packed into lists whose token lengths sum to ≤ 460.
5. Each list is translated as a batch.

The packer is the most careful piece of engineering in the repo. Danish news from a 10k dump includes long court and municipal pieces; Marian will silently truncate if you feed 2k tokens.

### Translation call

```python
source_tokens = [tokenizer.convert_ids_to_tokens(tokenizer.encode(sentence)) for sentence in text]
target_prefixes = [[tgt_lang] for _ in source_tokens]  # default tgt_lang='eng_Latn'
results = translator.translate_batch(source_tokens, target_prefix=target_prefixes)
translations = [tokenizer.decode(tokenizer.convert_tokens_to_ids(result.hypotheses[0][1:])) for result in results]
```

That pattern is the CTranslate2 **NLLB** recipe: force a language-code prefix and drop the first hypothesis token. OPUS-MT `da-en` is bilingual Marian. It does not speak `eng_Latn`. Forcing that string as a decoder prefix can insert a junk first token or degrade the hypothesis. I left it in because I started the file as an NLLB script and swapped the model path later. See [known-issues.md](known-issues.md).

`src_lang="dan_Latn"` is also passed into `AutoTokenizer.from_pretrained` for a tokenizer that has no NLLB language map. Transformers usually ignores unknown kwargs or warns; it is not a real language switch.

### Device

The translator uses `"cuda"` or `"cpu"` as a CTranslate2 device string. There is no `device_index` or compute-type (`int8`, `float16`) argument, so conversion precision is whatever `TransformersConverter.convert` defaulted to.

## 3. `summary.py` — English news T5

| Item | Value |
| --- | --- |
| Input | `translated_articles.csv` |
| Model | `mrm8488/t5-base-finetuned-summarize-news` |
| Output | `summarized_file_ml80_rp5.0.csv` |
| Article pack limit | 512 tokens |
| Generate | `num_beams=2`, `max_length=80`, `repetition_penalty=5.0`, `length_penalty=1.0`, `early_stopping=True` |

The filename encodes the two knobs I actually swept in the lab: summary max length (`ml`) and repetition penalty (`rp`). I do not have the other cells of that sweep in git. `rp=5.0` is aggressive; it was a reaction to T5 looping “the the the” on some translated leads.

### Map-reduce style summarization

Long English articles are split the same way as in `translate.py` (sentence pack under 512). **Each pack is summarized independently**, then the sub-summaries are joined with a space. That means:

- a 3,000-token article becomes several 80-token summaries concatenated
- the “summary” of a long piece can be longer than a Nordjylland lede (Nordjylland human summaries top out around 499 characters; this join has no global budget)
- there is no second-pass “summarize the summaries” step

For the course, that was acceptable: the silver label only had to be *a* compression, not a TV2 Nord-style one-liner.

### The ten-row slice

```python
df = pd.read_csv(input_file_path)[:10]
```

This is the single most important “did I actually generate 10k labels?” question. As committed, a naive rerun labels ten articles. I do not remember whether the slice was added after the full run (to make the file safe to demo) or before (and a full run lived only in an unsaved notebook). **Do not assume the silver set in `datasets/` — which is not in git — came from this exact file.**

## 4. `translate_back.py` — English summaries to Danish

| Item | Value |
| --- | --- |
| Input | `summarized_file_ml80_rp5.0.csv` |
| Required columns | `summary`, `body`, `id` |
| Model dir | `models/opus-mt-en-da_ct2` |
| Tokenizer | `Helsinki-NLP/opus-mt-en-da` |
| Output | `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`) |

`body` is passed through unchanged: it should still be the **original Danish** article from step 2, not the English translation. The English column is dropped. That is the correct pairing for fine-tuning: Danish document, Danish (silver) summary.

### Splitter is weaker than step 2

`split_into_sentences` here does not call `split_long_sentence`. A single English sentence over the budget is appended anyway and can overflow Marian. In practice summaries are short (`max_length=80` on T5), so this rarely mattered. The function also receives `max_length` (512) from `translate_article` rather than `text_max_length` (460). Off-by-10% and unused function arguments (`src_lang`, `tgt_lang`, `max_input_length` on `translate_article`) are leftovers from the NLLB draft.

The same `eng_Latn` / `dan_Latn` prefix pattern is used as in `translate.py`.

## 5. Manual split (not a script)

`finetune.py` does not create folds. I split `labeled_dataset_ml80_rp5.0.csv` myself into:

- `datasets/train_dataset.csv`
- `datasets/validation_dataset.csv`
- `datasets/test_dataset.csv`

There is no recorded seed, ratio, or stratification (for example by article length). The local `test_dataset.csv` is **not** Nordjylland test. It is a slice of silver labels. Confusing those two tests is the easiest way to lie to yourself about quality: silver-test ROUGE measures reconstruction of the pivot pipeline, not usefulness on human Danish summaries.

## 6. `finetune.py` — mT5-large on silver CSVs

| Item | Value |
| --- | --- |
| Base | `google/mt5-large` |
| Input columns | `body` → encoder, `summary` → labels |
| Truncation | 1024 source / 128 target tokens |
| Trainer output dir | `mt5-summarize-large` |
| Final save | `./large_model` (weights only via `save_pretrained`) |
| Epochs | 20 |
| Optimizer | Adafactor, lr `3e-4`, polynomial schedule, 1000 warmup, weight decay 0.01 |
| Batch | 8 / 8, no gradient accumulation |
| Precision | `fp16=True` |
| Generate @ eval | `generation_max_length=128`, `predict_with_generate=True` |
| Best checkpoint | `rouge_1_mid_fmeasure`, `save_total_limit=1`, `load_best_model_at_end=True` |

Generation config baked into `AutoConfig`:

- `min_length=9`
- `max_length=128`
- `length_penalty=0.8` (slightly prefer shorter)
- `no_repeat_ngram_size=3`
- `num_beams=4`
- `dropout_rate=0.1`

`compute_metrics` uses the deprecated `datasets.load_metric("rouge")` API and NLTK `sent_tokenize` with `"\n".join(...)` so the rouge scorer sees sentence boundaries. Only mid F is logged (not low/high confidence intervals, not precision/recall).

`trainer.train()` is called; there is no `trainer.evaluate()` on the silver test split after training. The script prints `tokenized_dataset["train"]` once as a sanity check.

Tokenizer is **not** saved next to `./large_model`. A later load with `google/mt5-small` (as `eval.py` and `use_model.py` do) is a real defect.

## 7. `use_model.py` — qualitative loop

| Item | Value |
| --- | --- |
| Dataset | `ScandEval/nordjylland-news-summarization-mini`, split `test` |
| Columns expected | `input_text`, `target_text`, `text_len`, `summary_len` |
| Weights | `small_model` |
| Tokenizer | `google/mt5-small` |
| Batch size | 2 |
| Samples printed | first 5 batches (up to 10 examples if the loader is full) |
| Generate | beams 2, `no_repeat_ngram_size=1`, `max_length=128` |

`no_repeat_ngram_size=1` forbids repeating any unigram. That is much harsher than the training config (`3`) and will force awkward synonym churn. I used it at the demo stage because early checkpoints copied “i i i”.

Printed “input” text is `split_dataset["test"]["input_text"][i]`, i.e. dataset row `i`, while predictions come from dataloader batch `i`. With `batch_size=2` those indices diverge after the first batch: the displayed article is not the article that was summarized. That is a display bug, not a training bug.

Target max length at tokenize time is 180, not the 128 used in `finetune.py` / `eval.py`.

## 8. `eval.py` — quantitative loop

| Item | Value |
| --- | --- |
| Dataset | `alexandrainst/nordjylland-news-summarization`, split `test` |
| Columns removed after tokenize | `input_text`, `target_text`, `text_len`, `summary_len` |
| Official HF columns (2024+ card) | `text`, `summary`, `text_len`, `summary_len` |
| Weights | `small_model` |
| Tokenizer | `google/mt5-small` |
| Eval batch | 64 |
| Metrics | ROUGE mid F (keys `rouge_{name}_mid_fmeasure`) + BERTScore mean P/R/F1 |

`datasets.load_metric` is the old API (`d216a1a` switched *back* to it from `evaluate.load` on 16 December 2023). It still worked on the course cluster; it is not what I would write now.

BERTScore is configured `lang='da'` and `model_type="xlm-roberta-large"`. That combination is reasonable for Danish: XLM-R has Danish, and forcing `lang` stops BERTScore from loading an English RoBERTa.

`dataloader_drop_last=True` drops a remainder batch, so the reported test size is `floor(N / 64) * 64`. For Nordjylland test (4,178) that discards 18 examples. Not fatal, but it is not the full official test set.

`output_dir="mt5-summarize-large"` is unused except as a Trainer requirement.

## 9. Data flow diagram (columns)

```text
10000_articles_without_linebreaks.csv
    id, article text
            │  translate.py
            ▼
translated_articles.csv
    id, body=article text, translated=EN
            │  summary.py
            ▼
summarized_file_ml80_rp5.0.csv
    id, body=DA, translated=EN, summary=EN
            │  translate_back.py
            ▼
labeled_dataset_ml80_rp5.0.csv
    id, body=DA, summary=DA silver
            │  manual split
            ▼
datasets/{train,validation,test}_dataset.csv
    id, body, summary
            │  finetune.py
            ▼
large_model/   +   mt5-summarize-large/checkpoint-*

# separate evaluation distribution
alexandrainst/... or ScandEval/...-mini
    human DA article + human DA summary
            │  eval.py / use_model.py
            ▼
printed metrics / printed generations
```

## 10. What I would extract into a real package

If this were more than a course dump, the next engineering step would be a single `pipeline/` package with:

- a YAML config for paths, max lengths, and generate kwargs
- one sentence-packer
- OPUS-MT translation **without** NLLB prefixes
- a `split_dataset.py` with a recorded seed
- saving tokenizer + generation config beside the student weights
- a single eval entry point that maps Nordjylland `text`/`summary` explicitly

I am not doing that in this documentation pass. The scripts stay as the 2023 artifact.
