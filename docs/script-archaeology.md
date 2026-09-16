# Script archaeology

Notes from reading the 2023 files as they sit on `main`. The study kit
does not patch these. It documents them so examples do not "fix" the
past in silence.

## Converter only exports one direction

`Ctranslate_converter.py` constructs `Helsinki-NLP/opus-mt-en-da` and
writes `models/opus-mt-en-da_ct2`. The `opus-mt-da-en` block is
commented out. `translate.py` still expects `models/opus-mt-da-en_ct2`.
A clean run of the README as written cannot start hop 1.

NLLB 3.3B / 600M conversions are also commented. The prefixes
`dan_Latn` / `eng_Latn` look like leftovers from that experiment.
OPUS-MT does not use NLLB language tokens. Whether CTranslate2 ignores
the prefix or emits a junk first piece is why both translate scripts
drop `hypotheses[0][1:]`.

## `summary.py` only scores ten rows

```
df = pd.read_csv(input_file_path)[:10]
```

The filename `summarized_file_ml80_rp5.0.csv` sounds like a full dump.
It is a ten-row slice unless someone deleted that slice before a real
run and forgot to commit the change.

## Column rename mid-pipeline

| stage | article column | summary column |
| --- | --- | --- |
| raw input | `article text` | — |
| after translate | `body` | — |
| after summary | `body` | `summary` (English) |
| after translate_back | `body` | `summary` (Danish) |

`translated` exists only in the middle two tables.

## Fine-tune and eval disagree on data and size

* `finetune.py` reads `datasets/{train,validation,test}_dataset.csv`
  with `body` / `summary`.
* `eval.py` ignores those files and loads a public HF dataset with
  `input_text` / `target_text`.
* `use_model.py` loads a *different* public set (the ScandEval mini).
* Train: `google/mt5-large` → `./large_model`.
* Eval: `AutoModelForSeq2SeqLM.from_pretrained("small_model")`.

A reader who trains with the README and then runs `eval.py` will miss
the weights they just saved.

## `datasets.load_metric` is the old API

`finetune.py` and `eval.py` call `datasets.load_metric("rouge")`.
Upstream moved this to the `evaluate` package. `eval.py` already
imports `evaluate` and then does not use it for ROUGE.

## Auth token flag

Both translate scripts pass `use_auth_token=False` into
`AutoTokenizer.from_pretrained`. That kwarg is deprecated in current
`transformers` (`token=False` is the replacement). Harmless in 2023.

## Device print vs translator device

The scripts print `torch.device("cuda" if ...)` and then construct
`ctranslate2.Translator(..., device="cuda" if ... else "cpu")`. The
tokenizer still runs on CPU. Fine, but the `device` variable in
`translate.py` is otherwise unused.
