# Danish News Summarization

Personal ITU final project (December 2023). **Not** work code. There is no employer, client, or proprietary data in this repository.

**Course:** Advanced Natural Language Processing and Deep Learning, IT University of Copenhagen  
**Author:** Sapphire Ran (`pang990801` / [sapphireran](https://github.com/sapphireran))  
**License:** MIT

The idea: manufacture Danish news summaries by pivoting through English, then fine-tune multilingual T5 on those silver pairs.

```text
Danish article  →  English article  →  English summary  →  Danish summary
   (unlabeled)      opus-mt-da-en        news T5           opus-mt-en-da
                                                              │
                                                              ▼
                                                         fine-tune mT5
                                                              │
                                                              ▼
                                              evaluate on Nordjylland (human)
```

The December 2023 tree is a lab notebook. Weights, the 10k article dump, and any ROUGE numbers were never committed. This 2026 pass adds **documentation and runnable examples** only. The original Python at the repo root is left as it was.

## Run something today (no GPU)

The only path that works on a clean clone:

```bash
python3 examples/validate_schema.py
python3 examples/inspect_samples.py
python3 examples/pack_report.py --id oesterhavn-kvote --budget 20
python3 examples/compare_hops.py --id lund-bageri
python3 examples/run_toy_pipeline.py --output /tmp/dns-toy --budget 40
python3 -m unittest discover -s tests -t . -v
```

Ten fictional Danish briefs live in [`examples/data/`](examples/data/README.md). The toy pipeline replays hand-written English / Danish strings for those ids and writes the same CSV shapes as `translate.py` → `summary.py` → `translate_back.py`. Details: [`examples/README.md`](examples/README.md).

## 2023 scripts (need data + models)

| Script | Role |
| --- | --- |
| [`Ctranslate_converter.py`](Ctranslate_converter.py) | Hugging Face Marian → CTranslate2. As committed, only `opus-mt-en-da`. |
| [`translate.py`](translate.py) | Danish dump → English (`models/opus-mt-da-en_ct2`). |
| [`summary.py`](summary.py) | English → English summary (news T5). Slices to **10 rows**. |
| [`translate_back.py`](translate_back.py) | English summary → Danish silver label. |
| [`finetune.py`](finetune.py) | `google/mt5-large` on `datasets/*.csv`. |
| [`use_model.py`](use_model.py) | Print a few generations from `small_model/`. |
| [`eval.py`](eval.py) | ROUGE + BERTScore on Nordjylland test. |

Contracts, including the converter / checkpoint / column mismatches: [`docs/script-contracts.md`](docs/script-contracts.md).

```bash
python Ctranslate_converter.py   # then also convert opus-mt-da-en
python translate.py              # 10000_articles_without_linebreaks.csv
python summary.py                # remove [:10] for a full run
python translate_back.py
python finetune.py               # datasets/{train,validation,test}_dataset.csv
python use_model.py
python eval.py
```

## Documentation

- [Documentation home](docs/README.md)
- [Method in one page](docs/method-in-one-page.md)
- [Examples guide](docs/examples-guide.md)
- [Dataset schema](docs/dataset-schema.md)
- [Script contracts](docs/script-contracts.md)
- [Chunking algorithm](docs/chunking-algorithm.md)
- [Toy pipeline](docs/toy-pipeline.md)
- [Hop error budget](docs/hop-error-budget.md)
- [Personal notes](notes/README.md)

## What is not in git

| Artifact | Why it is absent |
| --- | --- |
| `10000_articles_without_linebreaks.csv` | Large, not licensed here |
| `translated_articles.csv`, `summarized_file_*.csv`, `labeled_dataset_*.csv` | Regenerable, large |
| `datasets/*.csv` | Fine-tune splits, never committed |
| `models/*_ct2`, `small_model/`, `large_model/` | Downloaded or trained weights |
| A score table | The 2023 run did not leave one |

Public evaluation data is on Hugging Face (`alexandrainst/nordjylland-news-summarization`, ScandEval mini). Those human summaries are the **exam**, not the training labels this pipeline builds.

## Status

Honest snapshot:

- The method is intact and still a reasonable course project.
- Several root scripts disagree (checkpoint name, tokenizer size, Nordjylland columns, converter outputs).
- `summary.py` will not process 10k rows until `[:10]` is removed.
- The examples are fixtures plus a packer, not a second model stack.

## License

MIT. See [LICENSE](LICENSE). Third-party models and datasets keep their own licenses.
