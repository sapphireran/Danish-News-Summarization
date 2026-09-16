# Limitations and known traps

Personal checklist of things that will bite a re-run of the 2023
scripts. The original files are left as they were submitted.

## Converter / translator mismatch

`Ctranslate_converter.py` exports only `opus-mt-en-da`. `translate.py`
loads `models/opus-mt-da-en_ct2`. Re-enable the commented DA→EN block
or the first real pipeline step will fail on a missing directory.

## `summary.py` only scores ten rows

`df[:10]` is still in the committed file. A 10k-article labeling job
will look like it finished quickly and write a CSV with ten summaries.

## `split_long_sentence` splits on every comma

While the running character count is under the limit, a comma /
semicolon / colon flushes the chunk. News sentences with lists become
many tiny translator calls. See `examples/text_chunking.py` and
`python examples/chunking_demo.py --mode historical`.

## Token length vs character length

Long-sentence splitting uses `len(word) + 1`. Packing uses the OPUS or
T5 tokenizer. A chunk can still overflow the model after a “successful”
character split, or be unnecessarily short.

## NLTK Punkt is English

`nltk.sent_tokenize` is called on Danish source text. It usually
survives news prose but will misfire on `ca.`, `bl.a.`, `kl.` and
ordinal dates (`3. april`) unless Punkt has seen similar patterns.
The offline examples use `examples/danish_sentences.py` instead.

## Deprecated Transformers / Datasets APIs

The scripts still use:

- `use_auth_token=False` on `from_pretrained` (replaced by `token`)
- `evaluation_strategy` (renamed `eval_strategy` in recent Transformers)
- `datasets.load_metric` (moved to `evaluate.load`)
- `Seq2SeqTrainer(..., tokenizer=...)` (newer releases prefer
  `processing_class`)

A current `transformers` / `datasets` install may warn or error. The
versions that match the source most closely are sketched in
`requirements.txt`.

## Checkpoint name drift

`finetune.py` writes `./large_model` from `google/mt5-large`.
`use_model.py` and `eval.py` load `small_model` and tokenize with
`google/mt5-small`. Mixing a large-model checkpoint with the small
tokenizer (or the reverse) will run and produce garbage.

## Evaluation is out-of-domain by construction

Training labels are T5-on-English then OPUS back to Danish. The
reported test set is TV2 Nord / Nordjylland. Low ROUGE is not
automatically a failed train.

## Nordjylland column names moved

See [evaluation.md](evaluation.md). `eval.py` may `KeyError` on a
fresh download.

## No requirements lock, no seed, no split script

The repo as submitted has no `requirements.txt`, no data license for
the 10k dump, and no code that builds `datasets/*.csv` from the labeled
file. Reproducibility is “same knobs, same scripts”, not “same bytes”.

## Silver-label error pile-up

Each hop can drop or invent entities:

1. DA→EN mistranslates a Danish place or title.
2. T5, prompted as generic English news, drops the number that mattered.
3. EN→DA produces a fluent Danish sentence that is no longer true.

`repetition_penalty=5.0` is aggressive and can also starve T5 of
repeated but necessary tokens (party names, town names). Read a sample
of `labeled_dataset_ml80_rp5.0.csv` before spending a long mT5 run.

## Not production software

Paths are hardcoded. There is no CLI. Device selection is
`cuda` or `cpu` only. The project was a course deliverable, not a
library. The `examples/` package is the place for later, testable
helpers; it does not change the original scripts.
