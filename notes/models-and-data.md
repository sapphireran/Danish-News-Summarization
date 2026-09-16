# Models and data I actually named

Inventory of third-party objects referenced by the 2023 scripts or by these notes. Personal catalog. Check each Hub card before a rerun; cards move.

## Translation

### `Helsinki-NLP/opus-mt-da-en`

- Family: Marian / OPUS-MT, bilingual Danish → English.
- Why I wanted it: small, fast after CTranslate2, good Tatoeba-style scores on the card (BLEU ~63.6 da-en, not a news-domain guarantee).
- Used in: `translate.py` (tokenizer + expected CT2 dir).
- Converter line: commented out in `Ctranslate_converter.py`.

### `Helsinki-NLP/opus-mt-en-da`

- Marian English → Danish.
- Used in: `translate_back.py`, active converter path.
- Same caveat: Tatoeba ≠ TV2 Nord named entities.

### `facebook/nllb-200-distilled-600m` and `facebook/nllb-200-3.3B`

- Commented only.
- Why I considered them: one model, many languages, explicit `dan_Latn` / `eng_Latn`.
- Why I backed off: 3.3B is a different compute story; 600M distilled might have been enough, but OPUS was already converting cleanly and I was out of calendar.
- Residue: language-code prefixes still in the OPUS call sites.

## English summarization

### `mrm8488/t5-base-finetuned-summarize-news`

- T5-base fine-tuned for news summarization (English).
- Why: I wanted a specialist, not `t5-base` with a prompt I would forget to add.
- Knobs I treated as part of the identity: `max_length=80`, `repetition_penalty=5.0`.
- Risk: CNN/DM-ish style projected onto Danish municipal and crime news after MT.

## Student / eval

### `google/mt5-large`

- Multilingual T5, encoder–decoder, the intended student.
- Fine-tune script: `finetune.py`.
- Memory: `fp16`, batch 8, Adafactor — the largest model I was willing to train in the course window.

### `google/mt5-small`

- Used as tokenizer name in `eval.py` and `use_model.py`.
- Also the name `small_model` as a **directory**, which may or may not have been a small-model experiment.
- I do not treat small as the official student in these notes. Large is what `finetune.py` says.

### `xlm-roberta-large`

- BERTScore backbone in `eval.py`.
- Not trained. Downloaded at metric compute time.

## Datasets

### Local (not in git)

| File | Role |
| --- | --- |
| `10000_articles_without_linebreaks.csv` | Unlabeled Danish news, 10k rows implied by name |
| `translated_articles.csv` | After DA→EN |
| `summarized_file_ml80_rp5.0.csv` | After English T5 |
| `labeled_dataset_ml80_rp5.0.csv` | After EN→DA |
| `datasets/train_dataset.csv` | Silver train |
| `datasets/validation_dataset.csv` | Silver val (checkpoint metric) |
| `datasets/test_dataset.csv` | Silver test (unused by scripts after split) |

I do not record the newsroom that produced the 10k dump in this file because I cannot verify it from git.

### `alexandrainst/nordjylland-news-summarization`

- TV2 Nord article + summary pairs.
- Curator: Oliver Kinch, Alexandra Institute.
- License on card: CC0-1.0.
- Splits: 75,219 / 4,178 / 4,178.
- Fields on card: `text`, `summary`, `text_len`, `summary_len`.
- Used in: `eval.py` (test split).
- Commented leftover in `eval.py`: `ScandEval/nordjylland-news-summarization-mini`.

### `ScandEval/nordjylland-news-summarization-mini`

- Used in: `use_model.py` (test split).
- Expected fields in code: `input_text`, `target_text`, `text_len`, `summary_len`.
- Purpose: cheap qualitative loop.
- Availability: may change as ScandEval / EuroEval evolve.

## What I did not use (on purpose)

- **DaNewsroom / DanSumT5 weights** as training data or as a student init. I treated them as related work, not as a dependency. Initializing from DanSumT5 would have mixed *their* gold abstractive newsroom style with *my* silver pivot style. Interesting experiment; not this repo.
- **Nordjylland train** as supervision. Using it would collapse the project into standard supervised summarization.
- **OpenAI / commercial APIs** for labeling. I wanted an offline stack I could in principle rerun.

## Citation snippets I would put in a course report

I am not copying paper PDFs into this repo. The pointers:

- OPUS-MT / Marian: Helsinki-NLP model cards; Tiedemann et al. OPUS line of work.
- mT5: Xue et al., “mT5: A Massively Multilingual Pre-trained Text-to-Text Transformer.”
- T5: Raffel et al., “Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer.”
- ROUGE: Lin, ACL 2004.
- BERTScore: Zhang et al.
- DaNewsroom: Varab & Schluter, LREC 2020.
- Newsroom density/coverage: Grusky, Naaman, Artzi.
- DanSumT5: Kolding, Nymann, Hansen, Enevoldsen, Kristensen-McLachlan.
- Nordjylland: Alexandra Institute dataset card.

CTranslate2: OpenNMT / CTranslate2 documentation for the converter and the NLLB prefix recipe I misapplied.
