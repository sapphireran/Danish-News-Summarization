# Danish News Summarization

Personal ITU course project (Advanced Natural Language Processing and Deep
Learning, 2023). The task was Danish abstractive news summarization when a
large in-domain Danish article/summary corpus was not available.

The labeling idea is a pivot through English:

1. Translate Danish news to English with OPUS-MT.
2. Summarize the English text with an English news T5 model.
3. Translate the summaries back to Danish.
4. Fine-tune mT5 on the original Danish bodies and those silver labels.

The root `*.py` files are the original course scripts. They still hard-code
file names and expect local model directories. Newer notes live under
`docs/` and runnable no-weight demos live under `examples/`.

## Read this first

- [docs/pipeline.md](docs/pipeline.md) — stage map and length handling
- [docs/datasets.md](docs/datasets.md) — CSV contracts
- [docs/translation.md](docs/translation.md) — CTranslate2 / OPUS-MT
- [docs/training-and-eval.md](docs/training-and-eval.md) — mT5 recipe
- [docs/limitations.md](docs/limitations.md) — leftover course scars
- [docs/reproducing.md](docs/reproducing.md) — full run vs laptop demos
- [examples/README.md](examples/README.md) — fictional sample articles

## Examples without model weights

The sample rows are original fictional Danish news written for this
repository. They are not from the private course dump.

```
python3 -m unittest discover -s tests -v
python3 examples/inspect_csv_schema.py
python3 examples/chunk_sample_articles.py
python3 examples/simulate_labeling_pipeline.py
python3 examples/print_training_recipe.py
```

`danish_summarization/` holds the sentence-packing helper and the column
contracts those examples use.

## Original course workflow

These commands need the private 10k-article CSV and downloaded weights.
See [docs/reproducing.md](docs/reproducing.md) before you start.

### 1. Convert OPUS-MT to CTranslate2

```
python Ctranslate_converter.py
```

Uncomment the Danish-to-English converter first. As committed, the file
only writes `models/opus-mt-en-da_ct2`, while `translate.py` reads
`models/opus-mt-da-en_ct2`.

### 2. Translate the Danish dump to English

```
python translate.py
```

Input: `10000_articles_without_linebreaks.csv` with columns `id` and
`article text`.

### 3. Summarize the English articles

```
python summary.py
```

The committed script slices the frame to the first 10 rows. Remove `[:10]`
for a full run.

### 4. Translate summaries back to Danish

```
python translate_back.py
```

### 5. Fine-tune mT5

Split the labeled CSV into `datasets/train_dataset.csv`,
`datasets/validation_dataset.csv`, and `datasets/test_dataset.csv`, then:

```
python finetune.py
```

### 6. Inspect and score

```
python use_model.py
python eval.py
```

Those two scripts load `./small_model` and public Nordjylland news sets,
not the silver labels.

## Scope

Personal student code only. Do not add company data, internal prompts, or
private work notes to the sample files. The checked-in examples stay
fictional on purpose.

## License

MIT. See [LICENSE](LICENSE).
