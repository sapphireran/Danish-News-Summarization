# Models

Three pretrained families sit on the critical path. A fourth (`xlm-roberta-large`) is only used as a BERTScore backbone in `eval.py`.

## 1. Helsinki-NLP OPUS-MT (the pivot)

| Direction | Hub id | CTranslate2 folder the scripts want |
| --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `models/opus-mt-da-en_ct2` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `models/opus-mt-en-da_ct2` |

These are MarianMT models trained on OPUS bitext. They are small, fast, and good enough for news prose. They are **not** instruction models and they do not take NLLB language tags as a first-class input.

### Conversion

`Ctranslate_converter.py` as committed:

```python
opus_en_da_model = TransformersConverter("Helsinki-NLP/opus-mt-en-da")
output_dir_opus_en_da = "models/opus-mt-en-da_ct2"
opus_en_da_model.convert(output_dir_opus_en_da)
```

You also need the other direction. Uncomment the existing lines or run:

```python
from ctranslate2.converters import TransformersConverter

TransformersConverter("Helsinki-NLP/opus-mt-da-en").convert("models/opus-mt-da-en_ct2")
TransformersConverter("Helsinki-NLP/opus-mt-en-da").convert("models/opus-mt-en-da_ct2")
```

CTranslate2 writes a `model.bin` (or `model.safetensors` on newer releases) plus a `config.json` into that folder. `ctranslate2.Translator(model_path, device=...)` loads it.

### Tokenizers stay on the Hugging Face side

The course scripts load the *original* HF tokenizer even after conversion:

```python
tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-da-en", use_auth_token=False, src_lang="dan_Latn")
```

`src_lang="dan_Latn"` is an NLLB/M2M argument. Marian/OPUS tokenizers typically ignore it. It is harmless if ignored, misleading if you assume it selected a language pair.

### Why CTranslate2

Labeling 10k articles sentence-by-sentence through `model.generate` in Transformers is slow. CTranslate2 is a C++ runtime with fused ops and optional quantization. For this project it is a speed choice, not a quality choice. Do not mix a Transformers generate loop in one direction with CTranslate2 in the other unless you have compared outputs; decoding defaults differ.

### Commented NLLB experiments

The converter still has commented `facebook/nllb-200-3.3B` and `facebook/nllb-200-distilled-600m` lines. Translation helpers still look like NLLB (`target_prefix=[[tgt_lang]]`, drop first generated token). If you revive NLLB:

- convert *that* checkpoint,
- keep the language tags (`dan_Latn`, `eng_Latn`),
- expect a much larger disk and VRAM footprint.

If you stay on OPUS-MT, treat those prefixes as leftover API and verify they do not steal the first output token. See [troubleshooting.md](troubleshooting.md).

## 2. English news T5 (`mrm8488/t5-base-finetuned-summarize-news`)

Used only in `summary.py`.

| Item | Value |
| --- | --- |
| Architecture | T5-base, encoder–decoder |
| Language | English in, English out |
| Hub id | `mrm8488/t5-base-finetuned-summarize-news` |
| Input cap used here | 512 tokens |
| Generate cap used here | 80 tokens |
| Beams | 2 |
| Repetition penalty | 5.0 |
| Length penalty | 1.0 |

This checkpoint is a community fine-tune of T5 on news summaries. It is the “strong English teacher” the pivot design depends on. It will happily summarize *translated* Danish news, including translation artifacts. Garbage English in → confident English out.

### Prefixes

Some T5 checkpoints want a task prefix (`summarize: ...`). This particular news fine-tune is used in the course script *without* a prefix: `tokenizer.encode(text, ...)`. If you swap in vanilla `t5-base` or `google/flan-t5-base`, you will need the prefix and probably different generate knobs.

### Why not summarize Danish directly?

In 2023 there was no equally convenient Danish T5 news checkpoint of this strength. Multilingual T5 *can* summarize Danish zero-shot, but poorly. The project’s bet: a good English specialist + two OPUS hops beats zero-shot mT5. That bet is exactly what Nordjylland eval is for.

## 3. Google mT5 (the student model)

| Script | Hub id | Local folder |
| --- | --- | --- |
| `finetune.py` | `google/mt5-large` | writes `./large_model` |
| `use_model.py` | tokenizer from `google/mt5-small` | loads `small_model` |
| `eval.py` | tokenizer from `google/mt5-small` | loads `small_model` |

`mT5` is T5 pre-trained on mC4 (101 languages, including Danish). Fine-tuning it on Danish silver pairs is the actual “Danish summarizer” the project delivers.

### large vs small mismatch

This is the most important model-card note in the repo:

- Training is configured for **mT5-large**.
- Qualitative + quantitative eval is configured for a folder named **`small_model`** and a **mT5-small** tokenizer.

Those only line up if you *also* trained a small model and saved it as `small_model`, or if you change the eval scripts. Loading a large checkpoint with a small tokenizer (or the reverse) will appear to work and then emit garbage. After a large run, either:

```python
# eval.py / use_model.py
model_name = "google/mt5-large"
local_model_path = "large_model"
```

or train a small model and keep the current eval paths.

The example docs treat `small_model` as “whatever student checkpoint you actually trained.”

### Generation config baked into `AutoConfig`

`finetune.py` overwrites config before `from_pretrained`:

| Key | Value | Intent |
| --- | --- | --- |
| `min_length` | 9 | avoid empty / one-word summaries |
| `max_length` | 128 | short news abstract |
| `length_penalty` | 0.8 | mild preference for shorter beams |
| `no_repeat_ngram_size` | 3 | kill phrase loops |
| `num_beams` | 4 | a bit more search than the English teacher (2) |
| `dropout_rate` | 0.1 | regularize a 20-epoch run |

`use_model.py` does **not** reuse that config. It generates with `num_beams=2`, `no_repeat_ngram_size=1`, `max_length=128`. `no_repeat_ngram_size=1` forbids repeating any unigram, which is a very aggressive setting for Danish (articles and prepositions will fight it). Treat inspection output as a lower bound on fluency.

## 4. Metric backbones

`eval.py`:

- ROUGE via `datasets.load_metric("rouge")` (legacy API; `evaluate.load("rouge")` is the modern equivalent).
- BERTScore via `datasets.load_metric("bertscore")` with `lang='da'` and `model_type="xlm-roberta-large"`.

`xlm-roberta-large` is a download of its own. First eval run is slow. `finetune.py` only uses ROUGE at epoch end (no BERTScore) so the 20-epoch loop is cheaper.

## Model files that belong in `.gitignore`

Never commit:

- `models/*_ct2/`
- `large_model/`
- `small_model/`
- `mt5-summarize-large/`

They are reproducible from the hub ids above plus `finetune.py`.

## Swapping models later

If you revisit this personal project:

| Swap | What else must change |
| --- | --- |
| OPUS-MT → NLLB / MADLAD | converter, language tags, decode slice, VRAM |
| English T5 → FLAN-T5 / Llama | prefixes, licenses, generate API, chunk length |
| mT5-large → mT5-small or ByT5 | `model_name`, eval tokenizer, batch size |
| BERTScore XLM-R → a Danish encoder | `model_type` in `eval.py` |

Keep the CSV contracts stable when you swap models. That is why `examples/lib/schema.py` exists.
