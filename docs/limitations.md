# Limitations and known gaps

The scripts were a 2023 course hand-in, not a maintained library. This
page lists the issues that will bite first if you rerun them.

## Incomplete model conversion

`Ctranslate_converter.py` only converts `opus-mt-en-da`. `translate.py`
loads `models/opus-mt-da-en_ct2`. A clean clone cannot finish stage 1
until the commented da→en block is enabled.

## NLLB prefixes on Marian OPUS

Both translation scripts set `src_lang` / `tgt_lang` to `dan_Latn` and
`eng_Latn` and pass `target_prefix=[[tgt_lang], ...]` into
`translator.translate_batch`. Those codes belong to NLLB-200, which is
commented out in the converter. Marian OPUS-MT models already know
their direction from the checkpoint. The `[1:]` slice on hypotheses is
a workaround that assumes the first generated token is the prefix.

If you re-enable NLLB, the prefix API is correct and the OPUS paths
should drop it. Mixing the two is how you get a leading junk token or
an accidentally English “Danish” summary.

## `summary.py` is a 10-row demo

```python
df = pd.read_csv(input_file_path)[:10]
```

A full silver-label run requires deleting that slice. The output
filename (`ml80_rp5.0`) does not record how many rows were actually
scored.

## Train / eval model-size split

`finetune.py` writes `./large_model` from `google/mt5-large`.
`eval.py` and `use_model.py` load `small_model` with a
`google/mt5-small` tokenizer. Running the README top to bottom does not
produce a directory those two scripts can open.

## Column-name drift on Nordjylland-News

`eval.py` assumes ScandEval-style `input_text` / `target_text` on a
dataset whose public card lists `text` / `summary`. This will fail
closed if the Hub revision you download still uses the card names.

## Decoding policy drift

| Location | beams | no-repeat n-gram | max length |
| --- | --- | --- | --- |
| English T5 (`summary.py`) | 2 | (repetition_penalty 5.0) | 80 per chunk |
| mT5 config (`finetune.py`) | 4 | 3 | 128 |
| `use_model.py` | 2 | 1 | 128 |

`no_repeat_ngram_size=1` is especially harsh in Danish.

## Chunk summaries concatenated

A long article becomes several 80-token English summaries joined with
spaces, then translated. The fine-tune target can therefore be a
multi-sentence extractive collage, while Nordjylland-News references
are usually a single lede. That style gap is a ceiling on ROUGE.

## No seed, no split, no filtering

- Fine-tuning is unseeded.
- The labeled CSV is not split by any script.
- There is no length-ratio filter, language-id check, or
  source-overlap check on silver labels.
- `finetune.py` loads a test CSV and never evaluates it.

## Deprecated APIs

As of later Transformers / datasets releases:

- `datasets.load_metric` → `evaluate.load`
- `evaluation_strategy` → `eval_strategy`
- `tokenizer=` on `Seq2SeqTrainer` → `processing_class=`
- `use_auth_token` → `token`

The 2023 scripts will emit deprecation warnings and may eventually
break. Behavior described in these docs is the behavior of the files
as committed, not a promise about future library versions.

## Metric implementation

`compute_metrics` reloads the ROUGE (and in `eval.py`, BERTScore)
metric **on every call**. During a 20-epoch train that is one Hub/cache
hit per epoch, which is slow but works. Move the `load_metric` calls
to module scope if you retrain.

`eval.py` sets `dataloader_drop_last=True`, dropping a partial batch
from the official test score.

## Legal / data hygiene

The silver-label path starts from a local news dump that is not in
git. TV2 Nord text from Nordjylland-News should not be copied into
`examples/data/`. The sample corpus in this documentation is original
fiction.

## What these docs do not claim

They do not claim that the 2023 model beat DanSumT5, that the silver
labels are factual, or that the pipeline is safe to run over arbitrary
web text. They document a personal course repository so it can be
studied and extended.
