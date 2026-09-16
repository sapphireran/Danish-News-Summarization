# Limitations and leftover course scars

The root scripts were written under a deadline. This page lists the scars
that still matter when you reuse the project as a personal reference.

## Converter and forward model disagree

`Ctranslate_converter.py` writes `opus-mt-en-da`. `translate.py` reads
`opus-mt-da-en`. A clean checkout cannot translate Danish to English until
the commented da-en converter is enabled.

## NLLB prefixes on OPUS-MT

Both translation scripts pass `dan_Latn` / `eng_Latn` target prefixes and
drop the first generated token. That is NLLB behaviour left on an OPUS-MT
code path. Check a handful of outputs before trusting a full 10k run.

## `summary.py` only keeps ten rows

```
df = pd.read_csv(input_file_path)[:10]
```

This is the single most expensive silent footgun in the repo. The filename
`summarized_file_ml80_rp5.0.csv` does not mention the slice.

## Two different model directories

Fine-tuning saves `./large_model`. Inspection and evaluation load
`./small_model`. The tokenizer side of those scripts still names
`google/mt5-small`. Decide which experiment you are reproducing before you
compare numbers.

## Inspection alignment

`use_model.py` prints `input_text[i]` for batch `i` while the batch itself
contains two rows. Treat the printed article as a hint, not as a guaranteed
pair with the decoded gold summary.

## Metric APIs

`finetune.py` and `eval.py` call `datasets.load_metric`. `eval.py` also
imports `evaluate` and never uses it. On current `datasets` releases the
old loader may warn or fail. The replacement is `evaluate.load("rouge")`
and `evaluate.load("bertscore")`.

## `use_auth_token` and `src_lang`

`AutoTokenizer.from_pretrained(..., use_auth_token=False, src_lang=...)`
mixes an old auth flag with an NLLB-only language argument. It worked with
the 2023 Transformers pin. It may warn now.

## No train/validation split script

The labeling pipeline stops at one labeled CSV. The three files under
`datasets/` were created by hand. If you regenerate labels, write the split
down. Random row shuffles can put the same story's follow-up in both train
and validation.

## No dependency pin in the original project

The 2023 environment was a notebook-style mix of `transformers`,
`datasets`, `ctranslate2`, `nltk`, `pandas`, and `torch`. There was no
`requirements.txt` in the first commit. The one in this repository is a
later reconstruction, not the exact course conda env.

## Silver labels are not truth

Everything downstream inherits translation error, English-news style, and
back-translation drift. Nordjylland ROUGE is therefore a domain transfer
score as much as a summarization score.

## License and data

The code is MIT. The private 10k-article dump is not redistributed. The
sample CSVs under `examples/data/` are original fiction and can be copied
with the code. Nordjylland news has its own dataset license; check that
before republishing generations.
