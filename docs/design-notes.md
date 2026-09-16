# Design notes

Personal commentary on the 2023 course project. This is not a paper and it
is not a production design review. It is the reasoning I would want if I
reopened the repo a few years later.

## The problem the course actually posed

The assignment was to build a Danish summarization model when:

- High-quality Danish abstractive labels were scarce.
- English news summarizers were already decent.
- Fine-tuning mT5 on a few thousand pairs was feasible on a single GPU
  if the labels could be manufactured.

So the project is really two systems glued together:

1. A **label factory** (translate → summarize → translate back).
2. A **seq2seq learner** (mT5) that never sees English at train time.

That split is the most useful way to reread the scripts. Bugs in the label
factory become an upper bound on how good `finetune.py` can look on
in-domain silver-label ROUGE, and they can still leave Nordjylland News
scores mediocre.

## Why pivot through English

Alternatives that were on the table in 2023:

| Approach | Why it was rejected then |
| --- | --- |
| Train on Nordjylland News only | The public set is small once you hold out a test split. |
| Lead-3 extractive Danish baseline | Cheap, but not the deep-learning project the course wanted. |
| Zero-shot mT5 or FLAN-style prompting | Worked poorly on Danish news in our course experiments. |
| Hire annotators | Out of scope and budget for a course project. |
| Danish-only unsupervised methods | Harder to get a clean abstractive target. |

Pivoting through English buys a strong English news summarizer
(`mrm8488/t5-base-finetuned-summarize-news`) at the cost of two
translation hops. Those hops inject:

- named-entity drift (people and place names)
- register shift (Danish news style → English news style → Danish MT style)
- length distortion (chunk-then-concatenate summaries)
- occasional polarity or negation errors

The hope is that mT5, reading the original Danish `body`, can still learn
useful compression patterns even if individual silver labels are noisy.

## Why CTranslate2 instead of Transformers generate()

The label factory runs over ~10k articles, and many articles need several
512-token windows. CTranslate2 was the pragmatic choice:

- Lower memory than a Hugging Face `generate()` loop
- Fast batched decoding
- Easy CPU fallback for laptops

The cost is an extra conversion step and a slightly awkward tokenizer
round-trip (`encode` → tokens → CTranslate2 → `decode`). OPUS-MT was used
instead of NLLB because the NLLB converters are commented out in
`Ctranslate_converter.py` — 3.3B is far more VRAM than a course machine
typically had.

## Why mT5 and not a Danish-only encoder-decoder

mT5 was the default multilingual T5 available to the course. It already
had Danish in the pretraining mix, so a few thousand silver pairs could
steer it toward news compression without teaching the language from
scratch.

`finetune.py` uses `google/mt5-large`. `eval.py` and `use_model.py` load
`google/mt5-small` as the *tokenizer* and `small_model` as the weights.
That mismatch is leftover experiment debris: the large run was the main
training job, and a smaller checkpoint was used for quicker qualitative
checks. A later rerun should make the checkpoint name a single config
value.

## What I would change on a personal rerun

1. **One config file** for paths, model ids, and generation knobs. The
   2023 scripts hard-code everything.
2. **Convert both OPUS-MT directions** in `Ctranslate_converter.py`.
3. **Delete `df[:10]`** in `summary.py` or gate it behind a `--limit`.
4. **Keep English and Danish summaries in the labeled file** during
   debugging, then drop English only when writing the train split.
5. **Score the silver labels themselves** against a small human sample
   before spending a long mT5 run. If da→en→summary→da is already weak,
   fine-tuning will not rescue it.
6. **Evaluate on one frozen test set.** `eval.py` and `use_model.py`
   currently disagree about which Nordjylland News dump to use.
7. **Align checkpoint names.** Training writes `large_model`; eval reads
   `small_model`.
8. **Replace `datasets.load_metric`** with `evaluate.load`. The former
   was already deprecated in 2023.
9. **Record the train/val/test split script.** It is the missing stage
   between `translate_back.py` and `finetune.py`.
10. **Cap concatenated chunk summaries** so a long article does not
    become a silver label that is itself several paragraphs.

The examples in this repository implement (1), (4), and (9) in miniature
so those ideas can be tried without a GPU.

## What I would not change

- Keeping the original Danish `body` all the way through the factory.
  Training on translated English articles would test the wrong language.
- Holding out Nordjylland News from training. Using it only at eval time
  is the one methodological choice that still looks right.
- Treating the silver labels as *training fuel*, not as ground truth in
  the scientific sense.

## Course context

This was a 2023 ITU course final project, written quickly, with scripts
that were edited in place. The README at the time listed only the six
`python …` commands. These notes exist so the next personal checkout does
not have to reverse-engineer filenames from the source again.
