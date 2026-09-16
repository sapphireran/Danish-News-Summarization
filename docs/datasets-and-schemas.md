# Datasets and CSV schemas

Every stage uses a slightly different schema. The scripts do not validate columns. A missing or renamed field fails inside pandas or Hugging Face with a `KeyError`.

## Source corpus (not in git)

**File:** `10000_articles_without_linebreaks.csv`

The filename is the only documentation. The 2023 run used a dump of Danish news articles that had already had hard line breaks stripped so sentence tokenizers would see real sentences instead of layout fragments.

| Column | Type | Meaning |
| --- | --- | --- |
| `id` | string or int | Stable article id from the dump |
| `article text` | string | Full Danish article body. The space in the name is required. |

There is no headline column, no date, no outlet, and no gold summary at this stage.

`translate.py` does `df['article text'].tolist()` and `df['id'].tolist()`. Extra columns are ignored.

### What “without linebreaks” was for

Newspaper HTML and PDF extracts often insert `\n` in the middle of a clause. `nltk.sent_tokenize` then emits fragments that OPUS-MT translates poorly. The dump was pre-cleaned. If you rebuild a source file, collapse single newlines inside a paragraph and keep blank lines only if you truly have section breaks.

## After Danish → English

**File:** `translated_articles.csv`  
**Writer:** `translate.py`

| Column | Language | Meaning |
| --- | --- | --- |
| `id` | — | Copied from the source dump |
| `body` | Danish | Original article (`article text` renamed) |
| `translated` | English | Full-article OPUS-MT output, packs joined with spaces |

`summary.py` reads `translated` for the model and keeps `body` / `id` for later stages. It never translates `body` again.

## After English summarization

**File:** `summarized_file_ml80_rp5.0.csv`  
**Writer:** `summary.py`

| Column | Language | Meaning |
| --- | --- | --- |
| `id` | — | Copied |
| `body` | Danish | Original article |
| `translated` | English | Same as previous file |
| `summary` | English | T5 news summary, possibly several 80-token pieces concatenated |

If an article was split into *k* sub-articles, `summary` is `sub_1 + " " + ... + sub_k`. There is no delimiter that would let you recover the pieces.

Change the filename when you change `max_length` or `repetition_penalty`. The rest of the pipeline hardcodes this name, so update `translate_back.py` at the same time.

## After English → Danish (silver labels)

**File:** `labeled_dataset_ml80_rp5.0.csv`  
**Writer:** `translate_back.py`

| Column | Language | Meaning |
| --- | --- | --- |
| `id` | — | Copied |
| `body` | Danish | Original article (the fine-tune source) |
| `summary` | Danish | Back-translated silver summary (the fine-tune target) |

`translated` is discarded here on purpose. The fine-tune must not see English.

## Fine-tune splits

**Files:**

```
datasets/train_dataset.csv
datasets/validation_dataset.csv
datasets/test_dataset.csv
```

**Reader:** `finetune.py`

| Column | Used as |
| --- | --- |
| `id` | Dropped after tokenization (kept only so you can debug a row) |
| `body` | Encoder input, truncated to 1024 tokens |
| `summary` | Decoder labels, truncated to 128 tokens |

`finetune.py` tokenizes `summary` to **128** tokens even if the silver summary is longer. Concatenated multi-chunk English summaries that survive back-translation will be cut. That silently discards the tail of long articles' silver labels.

Suggested split policy if you recreate the files:

| Split | Fraction | Notes |
| --- | --- | --- |
| train | 0.80 | All silver pairs used for gradient steps |
| validation | 0.10 | Used every epoch for ROUGE-1 mid F |
| test | 0.10 | **Not used** by `finetune.py` after load. The object is built (`split_dataset['test']`) but never passed to the trainer. |

The unused silver test split was probably intended for an offline eval that never landed in git. `eval.py` scores a public set instead.

## Public evaluation sets

These are Hugging Face datasets. They are **human** (or at least editorially) summarized Danish news, not the silver labels.

### `ScandEval/nordjylland-news-summarization-mini`

Used by `use_model.py`.

| Column | Role in the script |
| --- | --- |
| `input_text` | Article, tokenized to 1024 |
| `target_text` | Gold summary, tokenized to 180 |
| `text_len` | Dropped |
| `summary_len` | Dropped |

The mini split is for qualitative prints, not for reporting a final number.

### `alexandrainst/nordjylland-news-summarization`

Used by `eval.py`.

Same column names. `eval.py` tokenizes `target_text` to 128, not 180. Generation length and label length therefore do not match `use_model.py`.

A commented line in `eval.py` shows an earlier attempt to eval on the mini set. Leave the full set for reported scores.

## Synthetic fixtures in this repo

[`../examples/data`](../examples/data) mirrors the schemas above with fictional Danish/English text:

| Fixture | Mirrors |
| --- | --- |
| `sample_source_articles.csv` | `10000_articles_without_linebreaks.csv` |
| `sample_translated_articles.csv` | `translated_articles.csv` |
| `sample_summarized.csv` | `summarized_file_ml80_rp5.0.csv` |
| `sample_labeled_dataset.csv` | `labeled_dataset_ml80_rp5.0.csv` |
| `sample_train_dataset.csv` | `datasets/train_dataset.csv` |
| `sample_validation_dataset.csv` | `datasets/validation_dataset.csv` |
| `sample_test_dataset.csv` | `datasets/test_dataset.csv` |
| `sample_public_eval.jsonl` | public eval columns `input_text` / `target_text` |

These rows are invented. They are not from Nordjylland-Posten or any scraped dump.

## Encoding and punctuation

All writers use `encoding='utf-8'` and `index=False`. Danish letters (`æ`, `ø`, `å`, `Æ`, `Ø`, `Å`) must survive every hop. If you open a CSV in Excel on a Danish Windows machine, it may re-save as Windows-1252 and corrupt the next pandas read. Re-read with `encoding='utf-8'` and refuse to commit a file that does not round-trip `å`.

Sentence splitting uses NLTK `punkt`. Danish and English both need the punkt model downloaded (`nltk.download('punkt')` is already in the scripts). For Danish, `punkt` is acceptable but not perfect; abbreviations such as `bl.a.`, `f.eks.`, and `kr.` can emit false sentence boundaries and therefore extra translation packs.

## Empty and broken rows

None of the scripts drop NA rows. A blank `article text` still goes through the translator and becomes a blank or garbage summary. Before a serious rerun, drop rows where `body` is null or shorter than a few sentences.

## Identifier stability

`id` is the only join key. Keep it unchanged from the source dump through the silver label file. If you deduplicate articles, do it once, up front, so you do not train on two silver summaries of the same body with different ids.
