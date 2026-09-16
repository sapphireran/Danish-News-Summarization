# Translation stage

Two hops use Helsinki OPUS-MT through CTranslate2. They share a packing idea and differ in direction, tokenizer, and which column they rewrite.

## Models

| Direction | Hugging Face id | CTranslate2 directory | Script |
| --- | --- | --- | --- |
| Danish → English | `Helsinki-NLP/opus-mt-da-en` | `models/opus-mt-da-en_ct2` | `translate.py` |
| English → Danish | `Helsinki-NLP/opus-mt-en-da` | `models/opus-mt-en-da_ct2` | `translate_back.py` |

OPUS-MT is a Marian NMT family. It is not NLLB. Commented NLLB converters in `Ctranslate_converter.py` are leftovers; the running scripts never load them.

### Conversion

```python
from ctranslate2.converters import TransformersConverter
TransformersConverter("Helsinki-NLP/opus-mt-en-da").convert("models/opus-mt-en-da_ct2")
```

Conversion is one-shot and writes a directory of CTranslate2 files. Re-run only when you change quantization or the upstream checkpoint. The checked-in converter does **not** currently emit the da-en directory — uncomment that block.

CTranslate2 picks CUDA when `torch.cuda.is_available()`, otherwise CPU. That matches how `Translator(..., device=...)` is constructed in both scripts.

### Tokenizers at runtime

CTranslate2 wants **token strings**, not raw text. Both scripts:

1. `tokenizer.encode(sentence)` with the matching Helsinki tokenizer
2. `convert_ids_to_tokens(...)`
3. `translator.translate_batch(source_tokens, target_prefix=...)`
4. Drop the first generated token (`hypotheses[0][1:]`) then `convert_tokens_to_ids` + `decode`

The `target_prefix` is `eng_Latn` or `dan_Latn`. Those look like NLLB language codes. Helsinki OPUS-MT da-en / en-da models are **bilingual** and do not use NLLB prefixes the way NLLB-200 does. The prefix is still passed. If you swap in a real NLLB CTranslate2 model, keep the prefix; if you see a stray `eng_Latn` in the decoded string, the drop-first-token logic failed or the model ignored the prefix.

`src_lang=` on `from_pretrained` is likewise an NLLB-style argument. For these OPUS-MT models it is effectively unused. Newer `transformers` may warn.

## Sentence packing

Marian OPUS-MT is trained around a 512-token encoder. The scripts set:

```text
max_length = 512
text_max_length = int(max_length * 0.9)   # 460
```

The 0.9 factor leaves room for special tokens and the target prefix.

### Algorithm (articles, `translate.py`)

1. `nltk.sent_tokenize` on the whole article (needs `punkt`).
2. Measure each sentence with `len(tokenizer.encode(..., add_special_tokens=True))`.
3. If a sentence is already longer than `text_max_length`, call `split_long_sentence`.
4. Greedy-pack sentences into lists whose token lengths sum to ≤ `text_max_length`.
5. Translate each list as a batch (`translate(list[str])` → `list[str]`).
6. Join with spaces, then join those chunks with spaces.

`split_long_sentence` does **not** count tokenizer tokens. It counts `len(word) + 1` on NLTK `word_tokenize` output and flushes on `,` / `;` / `:` if the chunk is still under the limit, or when the running character length exceeds the limit. That is a character heuristic used as if it were a token budget. It is good enough to stop Marian from dying on 2k-character run-on sentences; it is not aligned with the 460-token packer.

A cleaned-up, documented implementation of the same packing rules lives in `examples/chunking/article_chunker.py` and is exercised by `examples/chunking/demo_chunking.py`.

### Algorithm (summaries, `translate_back.py`)

Summaries are shorter, so `translate_back.py` skips `split_long_sentence`. It still packs sentences into 512-token groups (`split_into_sentences(..., max_length, tokenizer)` — note it passes `max_length` (512), not `text_max_length` (460)). That is an inconsistency with `translate.py`. For typical 80-token English summaries it never matters.

## Batch vs. article loop

Both scripts loop **one article (or one summary) at a time** with `tqdm`, and only batch *inside* that article (its packed sentence lists). They do not batch across articles. Throughput is therefore worse than a true corpus-level `translate_batch`. Fine for 10k news articles on one GPU; not what you would ship.

## Device and memory

- CTranslate2 on GPU is the intended path.
- CPU works and is slow. The examples do not call CTranslate2 at all.
- Do not load the Transformers Marian weights *and* the CTranslate2 translator if you are tight on VRAM. The scripts only keep the tokenizer from Transformers.

## Output hygiene

- Decodes keep punctuation attached however Marian emitted it. You may see spaces before Danish commas or missing space after periods when chunks are joined.
- `translate.py` `strip()`s the final article string. Internal double spaces can remain if a chunk was empty.
- There is no language-id filter on the output. A failed batch can write Danish back into `translated` or English into the silver `summary`.

## What to log if you extend this

Useful extra columns that the 2023 scripts do not write:

- `n_chunks` — how many packed groups the article needed
- `src_token_len` / `tgt_token_len`
- `translator_device`
- converter git / CTranslate2 version

`examples/data/translated_articles.sample.csv` shows the *shape* of a successful hop, with original (not scraped) text.
