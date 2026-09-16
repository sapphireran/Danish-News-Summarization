# Script archaeology

How to read the December 2023 files without a GPU, without the 10k dump,
and without changing them.

## The seven files

| file | role | hardcoded I/O |
| --- | --- | --- |
| `Ctranslate_converter.py` | HuggingFace → CTranslate2 | writes `models/opus-mt-en-da_ct2` only |
| `translate.py` | Danish → English | reads `10000_articles_without_linebreaks.csv` (`id`, `article text`); writes `translated_articles.csv` |
| `summary.py` | English news T5 | reads `translated_articles.csv` **`[:10]`**; writes `summarized_file_ml80_rp5.0.csv` |
| `translate_back.py` | English → Danish | reads that summarized file; writes `labeled_dataset_ml80_rp5.0.csv` (`id`, `body`, `summary`) |
| `finetune.py` | mT5-large | reads `datasets/{train,validation,test}_dataset.csv`; saves `./large_model` |
| `use_model.py` | qualitative generations | loads `./small_model`; Hub mini split |
| `eval.py` | ROUGE + BERTScore | loads `./small_model`; Hub full test split |

`python3 -m kystlinje schemas` prints the same contracts.

## Scars left unpatched

**Converter direction.** The da→en conversion is commented out. A
literal run of the README’s step 1 does not produce the directory
`translate.py` expects (`models/opus-mt-da-en_ct2`).

**NLLB language prefixes on OPUS-MT.** `translate.py` builds
`target_prefix=[[tgt_lang]]` with `eng_Latn`. That prefix is an NLLB
convention. OPUS-MT does not use FLORES codes. The lines are leftover
from the commented NLLB converters at the top of
`Ctranslate_converter.py`.

**Ten-row summarizer.** `df = pd.read_csv(input_file_path)[:10]` means
the committed `summary.py` labels a postcard, not a corpus. Anyone who
actually produced 10k silver labels used a local edit that is not in
git.

**Large train, small eval.** `finetune.py` writes `./large_model`.
`eval.py` and `use_model.py` load `./small_model`. The directory names
do not meet.

**Two Hub eval sets.** `eval.py` uses
`alexandrainst/nordjylland-news-summarization`. `use_model.py` uses
`ScandEval/nordjylland-news-summarization-mini`. Same family, not the
same split.

**`datasets.load_metric`.** Both metric functions call the deprecated
loader for `rouge` and `bertscore`. A 2026 rerun would use
`evaluate.load`.

**Character budget inside a token packer.** `split_long_sentence`
increments `current_length` by `len(word)+1` while the outer packer
asks the HuggingFace tokenizer for subword counts. `kystlinje pack`
reproduces the character path so the quirk is visible.

## What a 2023 run would have touched on disk

```
10000_articles_without_linebreaks.csv   # never committed
models/opus-mt-da-en_ct2/               # expected, not produced by the converter as committed
models/opus-mt-en-da_ct2/               # produced by the converter
translated_articles.csv
summarized_file_ml80_rp5.0.csv
labeled_dataset_ml80_rp5.0.csv
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
mt5-summarize-large/                    # Trainer output_dir
large_model/                            # explicit save
small_model/                            # what eval loads
```

`.gitignore` keeps those artefacts off GitHub if anyone reruns the GPU
scripts locally.
