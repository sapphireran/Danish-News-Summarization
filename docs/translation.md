# Translation

The labeling pipeline uses Helsinki-NLP OPUS-MT through CTranslate2. This
page records the conversion step, the runtime calls, and the places where
the original scripts still show earlier NLLB experiments.

## Model conversion

`Ctranslate_converter.py` wraps `ctranslate2.converters.TransformersConverter`.
As committed, only the English-to-Danish model is converted:

```
Helsinki-NLP/opus-mt-en-da  ->  models/opus-mt-en-da_ct2
```

The Danish-to-English converter is in the file but commented out:

```
Helsinki-NLP/opus-mt-da-en  ->  models/opus-mt-da-en_ct2
```

`translate.py` loads `models/opus-mt-da-en_ct2`. Before a forward pass you
must uncomment the da-en block and run the converter again. The NLLB 3.3B
and 600M paths are also commented out. They are leftovers from a speed and
quality comparison that did not become the final pipeline.

Conversion is a one-time download plus a local rewrite. The resulting
directories are large and are gitignored.

## Runtime translation

Both `translate.py` and `translate_back.py` do the same four steps:

1. Load a CTranslate2 `Translator` from a local directory.
2. Load the matching Helsinki-NLP tokenizer from Hugging Face.
3. Encode each sentence to tokens, then to token strings.
4. Decode the first hypothesis after dropping the first generated token.

The drop of `hypotheses[0][1:]` assumes the first generated token is a
target-language prefix. That is the NLLB convention. OPUS-MT does not use
`dan_Latn` / `eng_Latn` prefixes in the same way. The scripts still pass
those prefixes as `target_prefix` and still skip the first token. On a
fresh run, compare a few decoded sentences against `hypotheses[0]` without
the skip. If the first word of every output is missing, remove the `[1:]`
slice.

## Forward pass: Danish to English

`translate.py` settings:

- input column: `article text`
- model directory: `models/opus-mt-da-en_ct2`
- tokenizer: `Helsinki-NLP/opus-mt-da-en`
- working budget: 460 tokens
- output: `translated_articles.csv`

Sentence packing uses NLTK `punkt` plus the comma/word splitter documented
in [pipeline.md](pipeline.md). The example script
`examples/chunk_sample_articles.py` shows the same packing on the sample
CSV without calling CTranslate2.

## Backward pass: English to Danish

`translate_back.py` settings:

- input column: `summary`
- model directory: `models/opus-mt-en-da_ct2`
- tokenizer: `Helsinki-NLP/opus-mt-en-da`
- packing limit: 512 tokens, no 0.9 margin
- output: `labeled_dataset_ml80_rp5.0.csv`

Summaries are short, so one batch per row is the common case. The script
still splits on sentences in case a concatenated multi-window English
summary is longer than expected.

## English summarization is not translation

`summary.py` sits between the two translation scripts. It is an English
seq2seq news model, not OPUS-MT:

- checkpoint: `mrm8488/t5-base-finetuned-summarize-news`
- `num_beams=2`
- `max_length=80`
- `repetition_penalty=5.0`
- `length_penalty=1.0`
- `early_stopping=True`

Each packed English window gets its own 80-token summary. Those pieces are
joined with spaces. A long feature can therefore produce a Danish target
that is a chain of leads rather than one abstract. That is visible in
`examples/data/sample_summarized.csv`.

The `[:10]` slice at the top of `summary.py` is the most important
operational caveat in the repo. Leave it in place only when you are testing
the example-sized workflow.

## Practical run order

1. Uncomment the da-en converter.
2. `python Ctranslate_converter.py`
3. Confirm both `models/opus-mt-da-en_ct2` and `models/opus-mt-en-da_ct2`
   exist.
4. `python translate.py`
5. Remove the `[:10]` slice in `summary.py` if you want the full dump.
6. `python summary.py`
7. `python translate_back.py`
8. Split `labeled_dataset_ml80_rp5.0.csv` into the three `datasets/` files.

The example script `examples/simulate_labeling_pipeline.py` walks the same
order on the fictional sample rows and only uses the checked-in CSVs. It
does not call the models.

## Things that commonly break

- Missing `punkt`: both translation scripts call `nltk.download('punkt')`
  at import time. On a machine without network egress that line fails
  before any translation starts.
- `use_auth_token=False` is the older Transformers argument. Newer releases
  prefer `token=False`.
- `src_lang=` on `from_pretrained` is an NLLB tokenizer argument. OPUS-MT
  tokenizers usually ignore it, but a future Transformers release might not.
- CTranslate2 and PyTorch CUDA builds must match the installed driver. A
  CPU fallback works for the sample-sized examples but not for 10k articles
  in a reasonable time.
