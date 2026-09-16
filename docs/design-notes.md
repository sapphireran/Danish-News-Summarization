# Design notes and known mismatches

Personal notes from rereading the 2023 scripts. These are not a roast of the course deadline code; they are a list of things that will surprise a future rerun.

## Why pivot through English

In 2023, a ready Danish abstractive summarizer with a large open training set was not the default choice for a one-term project. English news T5 checkpoints *were* easy to pull. The bet:

> Round-trip translation noise < benefit of an English news summarizer’s pretrain.

That bet is the whole project. If the English summarizer is mediocre on machine-translated Danish news (it will be: MT output is flatter than real English journalism), the silver labels inherit that mediocrity, and mT5 learns to imitate it.

## Why CTranslate2 instead of `model.generate` for MT

Throughput. Labeling 10k articles with sentence packing means many batched short sequences. CTranslate2 was the low-friction accelerator. The cost is a second weight format and a converter script that drifted out of sync with `translate.py`.

## Converter / translator drift

`Ctranslate_converter.py` writes `opus-mt-en-da` only.

`translate.py` reads `opus-mt-da-en_ct2`.

A clean clone cannot finish stage 1 without uncommenting the other conversion. This is the highest-priority rerun fix.

## NLLB prefixes on OPUS-MT

```python
target_prefixes = [[tgt_lang] for _ in source_tokens]
results = translator.translate_batch(source_tokens, target_prefix=target_prefixes)
```

and later:

```python
tokenizer.decode(tokenizer.convert_tokens_to_ids(result.hypotheses[0][1:]))
```

The `[1:]` skip assumes the first generated token is the language tag. For NLLB that is correct. For OPUS-MT the first token is usually part of the sentence, so the pipeline may drop the first subword of every pack.

If a 2023 output file looks like it is missing word onsets, this is the first place to look.

## Character length vs token budget in `split_long_sentence`

```python
current_length += len(word) + 1
...
elif current_length >= max_length:  # max_length is a token budget (~460)
```

Danish compound words can be long characters and few BPE tokens, or the reverse (names, numbers). The splitter is a heuristic, not a token-accurate packer. The outer loop *does* measure tokens after the split, so packs should still stay near the budget, but you can get more fragments than necessary.

## `summary.py` processes ten rows

```python
df = pd.read_csv(input_file_path)[:10]
```

Easy to miss. A “full” labeling job that finishes in minutes is a red flag.

## Filename as hyperparameter log

`summarized_file_ml80_rp5.0.csv` is a good habit. The rest of the filenames (`translated_articles.csv`, `labeled_dataset_ml80_rp5.0.csv`) only record some of the knobs. The English file name is not propagated backward to the translation step.

## Column rename `article text` → `body`

Harmless, but every new script has to remember which name is valid at which stage. There is no shared schema module.

## `finetune.py` loads a test set it never uses

`test_dataset` is in the `DatasetDict` and then ignored. Either wire it into a final `trainer.evaluate()` or stop loading it.

## Train `mt5-large`, eval `small_model`

The eval/demo scripts will not see a fresh `finetune.py` run unless you copy weights. Directory names should be one of:

- always `./large_model`, or
- always `./small_model` after an `mt5-small` train, or
- a single `--model-path` flag (none exists today).

Tokenizer `from_pretrained("google/mt5-small")` while loading another size’s weights is the same class of bug.

## `use_model.py` print alignment

`input_text[i]` vs `batch_size=2` is documented in [evaluation.md](evaluation.md). Qualitative examples in any old report should be re-checked.

## `no_repeat_ngram_size=1` at demo time

Forbids repeating any word. Danish cannot state “den den” but it also cannot repeat `i`, `på`, `er`. Outputs will look telegraphic compared to the training decode (`no_repeat_ngram_size=3`).

## `eval.py` metric key names

The comprehension

```python
{f'rouge_{key}_mid_fmeasure': value.mid.fmeasure for key, value in rouge.items()}
```

produces `rouge_rouge1_mid_fmeasure`, not `rouge_1_mid_fmeasure`. Fine-tune and eval logs are not drop-in comparable.

## Deprecated APIs

| Call | Problem |
| --- | --- |
| `use_auth_token=False` | Removed/renamed in recent Transformers |
| `datasets.load_metric` | Moved to `evaluate` |
| `evaluation_strategy=` | Newer Transformers prefer `eval_strategy` |
| `Seq2SeqTrainer(..., tokenizer=)` | Newer versions want `processing_class` |

A 2026 environment will warn loudly. The algorithm is the same.

## No shared library

`split_long_sentence` and `split_into_sentences` are copy-pasted through `translate.py` and `summary.py`, with a simpler variant in `translate_back.py`. The examples folder reimplements one canonical version in `examples/text_chunking.py` so the behavior can be discussed without importing torch.

## Silver-label failure modes (content, not code)

These showed up conceptually even when the scripts ran cleanly:

1. **Entity drift.** OPUS-MT can respell Danish names on the way out and again on the way back.
2. **Lost negation.** A single dropped *ikke* flips a summary.
3. **Length inflation.** Chunk-wise T5 + concatenation produces a “summary” that is a list of ledes, not one abstract.
4. **Register.** MT English is simpler than the T5 news domain; T5 then writes generic AP-style English; back-translation writes generic Danish. mT5 learns that generic Danish.
5. **Domain shift at eval.** Nordjylland editorially written summaries are not translationese. A model that faithfully clones silver labels can look worse on the public set than a model that barely trained.

## What I would change first on a personal rerun

1. Convert both OPUS directions in `Ctranslate_converter.py`.
2. Remove NLLB prefixes when using OPUS-MT; stop skipping `hypotheses[0][1:]`.
3. Delete `[:10]` or make it a `LIMIT` env var defaulting to no limit.
4. Save tokenizer + weights in one directory; point every script at it.
5. Add argparse for input/output paths.
6. Filter empty / too-short bodies before translation.
7. Fix `use_model.py` indexing.
8. Write metrics JSON next to the checkpoint.

The examples in this repo implement (2) in spirit (no fake language tags), (3) as an explicit `--limit`, and (5) as path arguments, without claiming to replace the course scripts.
