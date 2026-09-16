# Translation stages

Two scripts move text across the language barrier:

| Script | Direction | CTranslate2 directory | Tokenizer |
| --- | --- | --- | --- |
| `translate.py` | Danish → English | `models/opus-mt-da-en_ct2` | `Helsinki-NLP/opus-mt-da-en` |
| `translate_back.py` | English → Danish | `models/opus-mt-en-da_ct2` | `Helsinki-NLP/opus-mt-en-da` |

Both use Helsinki-NLP OPUS-MT, not NLLB. The NLLB converters are present
only as comments in `Ctranslate_converter.py`.

## Converting checkpoints

```bash
python Ctranslate_converter.py
```

`TransformersConverter("Helsinki-NLP/opus-mt-en-da")` downloads the
Hugging Face weights and writes a CTranslate2 model directory.

The committed file only converts English → Danish. Uncomment the
`opus-mt-da-en` block before running `translate.py`:

```python
opus_da_en_model = TransformersConverter("Helsinki-NLP/opus-mt-da-en")
output_dir_opus_da_en = "models/opus-mt-da-en_ct2"
opus_da_en_model.convert(output_dir_opus_da_en)
```

Conversion is idempotent only if the output directory is empty. If a
partial convert is left behind, delete the directory and rerun.

## How a batch is translated

The decode path is the same in both scripts:

1. `tokenizer.encode(sentence)` → token ids
2. `tokenizer.convert_ids_to_tokens(...)` → CTranslate2 source tokens
3. `translator.translate_batch(...)` with a `target_prefix`
4. Drop the first generated token (the language prefix)
5. `tokenizer.convert_tokens_to_ids` + `tokenizer.decode`

`target_prefix` is set to `eng_Latn` or `dan_Latn`. Those are NLLB-style
language codes. OPUS-MT models do not use the same prefix scheme. In
practice the extra prefix token is often treated as a BOS-like symbol and
then stripped with `[1:]`. If a later ctranslate2 / tokenizer pairing
starts emitting a visible `eng_Latn` at the start of every sentence, the
prefix list is the first thing to remove.

`use_auth_token=False` is a Transformers v4-era argument. Newer
`transformers` wants `token=False` or no auth argument at all.

## Sentence packing

OPUS-MT was trained at 512 tokens. The scripts keep a safety margin:

```python
max_length = 512
text_max_length = int(max_length * 0.9)  # 460
```

`translate.py` does more work than `translate_back.py` because full news
articles are long:

1. `nltk.sent_tokenize` on the article.
2. If a single sentence encodes to more than 460 tokens, split on
   commas / semicolons / colons, then on raw word overflow.
3. Pack consecutive sentences into a window whose token counts sum to
   ≤ 460.
4. Translate each window as a batch of sentences.
5. Join translations with spaces.

`translate_back.py` skips the long-sentence splitter. Summaries are
usually short enough that `sent_tokenize` plus packing is enough. If a
future summarizer emits a 600-token run-on, this stage will overflow.

The packing algorithm is reconstructed in
`examples/scripts/chunk_text.py` so it can be unit-tested without
loading OPUS-MT.

### Length accounting caveat

Packing uses `len(tokenizer.encode(..., add_special_tokens=True))` per
sentence and **adds those lengths**. Special tokens are therefore counted
once per sentence, not once per window. The 0.9 margin exists partly to
absorb that double-counting. If you retune `text_max_length` upward,
watch for CTranslate2 max-length errors before celebrating throughput.

## Device selection

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
translator = ctranslate2.Translator(model_path, device="cuda" if ... else "cpu")
```

`torch` is only used as a CUDA probe. CTranslate2 does the work. A
machine with CUDA but an incomplete CTranslate2 GPU build will print
`Using device: cuda` and then fail inside `Translator`. In that case
force `device="cpu"`.

## Quality failure modes

These showed up when spot-checking silver labels in 2023:

- **Names.** Danish middle names and compound place names get English
  spellings or dropped letters.
- **Quotations.** Closing quotes sometimes attach to the wrong speaker
  after a window boundary.
- **Numbers and dates.** `12. marts` vs `March 12` is usually fine;
  `1.500` (Danish thousand separator) can become `1.5`.
- **Domain terms.** Local politics and sports nicknames are often
  translated too literally on the way to English and then again on the
  way back.
- **Window seams.** Two adjacent windows can repeat a clause or drop
  the sentence that sat on the boundary if the splitter cut on a comma.

When debugging, keep a side-by-side table of `body`, `translated`,
English `summary`, and Danish `summary` for 20 random ids. The examples
inspector can print those columns once the CSVs exist.

## Runtime expectations (order of magnitude)

On a single consumer GPU, da→en over 10k news articles was an
hours-scale job in 2023, not a minutes-scale job. CPU-only is
substantially slower. The English→Danish hop is faster because it
translates summaries, not full articles.

Do not run these scripts against `examples/data/sample_articles.csv`
unless you also change the hard-coded filenames. Use
`examples/scripts/dry_run_pipeline.py` for contract checks instead.
