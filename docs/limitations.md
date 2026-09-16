# Limitations and script quirks

The 2023 code worked well enough to finish a course project. It is not a
product pipeline. These are the issues that matter if you reuse it for
another personal experiment.

## Silver labels are not facts

Every training target has passed through two translation models and an
English news summariser. Typical damage:

- **Numbers drift.** "op mod 18.000" can become "thousands" and come back
  as "mange tusinde".
- **Entities blur.** Danish compounds and local toponyms are the first
  tokens OPUS-MT mishandles. mT5 then learns the mishandled form.
- **Stance flattens.** T5-base news checkpoints like a neutral lede.
  Quotes, conflict, and "men" constructions get dropped.
- **Concatenated ledes.** Long articles become several 80-token summaries
  glued together. The silver target can read like a bullet list without
  bullets.

Evaluating on Nordjylland News (human labels, different outlet) is the
main defence. It does not fix the training signal.

## `summary.py` only processes ten rows

```python
df = pd.read_csv(input_file_path)[:10]
```

This is still in the committed file. A labelling pass on the 10k dump
must delete the slice. The example fixtures already have ten rows, so
the offline walkthrough is not affected.

## Only one OPUS-MT model is converted

`Ctranslate_converter.py` converts `opus-mt-en-da`. The da→en block is
commented out, but `translate.py` loads `models/opus-mt-da-en_ct2`. A
clean checkout cannot finish step 2 without editing the converter.

## Language prefixes on a bilingual model

`translate.py` and `translate_back.py` still build NLLB-style
`target_prefix` lists (`eng_Latn`, `dan_Latn`). Those prefixes were meant
for the commented NLLB converters. On OPUS-MT they force the decoder to
start from a token the model was not trained to expect. If back-translated
summaries look truncated, try calling `translate_batch` without
`target_prefix`.

## Mixed character / token budgets

`split_long_sentence` uses `len(word) + 1`. The packer uses tokenizer
length (or whitespace tokens in the examples package). See
[silver-label-pipeline.md](silver-label-pipeline.md).

## `translate_back.py` does not split overflowing sentences

`translate.py` and `summary.py` break a too-long sentence into chunks.
`translate_back.py` only packs whole sentences; a long English summary
sentence is encoded as-is. In practice the English T5 outputs are short,
so this rarely fires. It is still an asymmetry.

## Evaluation paths assume `small_model`

`finetune.py` writes `./large_model`. `eval.py` / `use_model.py` read
`small_model`. That mismatch is easy to miss after a long training job.

## Deprecated metric API

`datasets.load_metric` is used in both `finetune.py` and `eval.py`.
Current `datasets` wants `evaluate.load`. Behaviour is the same for
`rouge` and `bertscore` today; it may disappear later.

## `use_auth_token=False`

The translation scripts pass the old `use_auth_token` kwarg into
`AutoTokenizer.from_pretrained`. Recent `transformers` renamed this to
`token`. It is harmless when you are pulling public OPUS-MT, and it will
warn on new versions.

## No licence for the 10k dump

The code is MIT (see `LICENSE`). The original Danish article dump is not
in the repository and is not covered by that licence. The committed
`examples/data` stories are invented and can be reused with the code.

## What the new examples do not claim

The offline lexical scores on `sample_eval_pairs.csv` are not a
reproduction of the 2023 Nordjylland News numbers. They only prove that
the documentation helpers run.
