# Related work (personal reading list)

This is the shelf I would put under the 2023 method. It is not a conference
survey and it does not cite employer memos.

## Sequence-to-sequence summarization

- **T5** (Raffel et al., 2020) treats every text problem as text-to-text. The
  English teacher in `summary.py` is a T5 checkpoint fine-tuned on news.
- **mT5** (Xue et al., 2021) is the multilingual sibling. `finetune.py` starts
  from `google/mt5-large` (the student) while `eval.py` / `use_model.py` name
  `google/mt5-small` as the tokenizer host. That mismatch is a scar, not a
  finding.
- **BART** (Lewis et al., 2020) and **PEGASUS** (Zhang et al., 2020) are the
  usual English abstractive baselines. They never entered this repo. I mention
  them so I do not pretend mT5 was the only student worth trying.
- **Pointer-generator** (See et al., 2017) is the extractive/abstractive hinge
  the course lectures used. Lead-k and TextRank are the even earlier hinge.

## Translation as infrastructure

- **OPUS-MT** (Tiedemann & Thottingal, 2020) supplies `Helsinki-NLP/opus-mt-da-en`
  and `opus-mt-en-da`. `Ctranslate_converter.py` wraps them in CTranslate2.
- **NLLB-200** (Team NLLB, 2022) is sitting in comments in the converter. The
  live translate scripts still pass `dan_Latn` / `eng_Latn` prefixes, which is
  NLLB's API, not OPUS-MT's. See [script-scars.md](script-scars.md).
- **Back-translation** (Sennrich, Haddow, Birch, 2016) is the closest classical
  name for "translate, do a thing, translate back". The thing in the middle
  here is a summarizer, so errors compound instead of averaging out.

## Cross-lingual summarization

The 2023 hop is a poor man's cross-lingual summarizer: Danish in, Danish out,
English in the middle. Proper XLS work (WikiLingua, XWikis, NCLS-style
encoder–decoder models) trains the hop as one model. I did not. I chained
three models and hoped the seams would not show. The [error catalog](error-catalog.md)
is the seam.

## Evaluation

- **ROUGE** (Lin, 2004) is n-gram and LCS overlap. The trainer used
  `datasets.load_metric("rouge")` and kept the mid F-measure. The lab
  reimplements ROUGE-1/2/L so a clone can compute overlap without that stack.
  See [metrics-from-scratch.md](metrics-from-scratch.md).
- **BERTScore** (Zhang et al., 2020) is in `eval.py` with `lang='da'` and
  `xlm-roberta-large`. It is the right *idea* for Danish morphology. It is
  also heavy, so the lab does not call it.
- **ScandEval** publishes a Nordjylland mini split that `use_model.py` loads.
  Column names there (`input_text`, `target_text`) do not match the official
  Alexandra card (`text`, `summary`). [nordjylland.md](nordjylland.md) keeps
  the two contracts apart.

## Danish NLP context

- **Nordjylland News Summarization** (Kinch / Alexandra Institute; TV2 Nord;
  CC0) is the public pair set.
- **DaNLP** and the broader ScandEval suite are the 2023-era places one went
  to see whether a Danish model was more than a demo.
- There is still no large, clean, editor-written Danish CNN/DM equivalent in
  this repository. That absence is why silver labels felt tempting.

## Extractive baselines the course skipped

- **Lead-k** is the unreasonably strong news baseline in English. Danish
  news desks also front-load. The lab measures that on fiction.
- **TextRank** (Mihalcea & Tarau, 2004) is graph centrality on sentence
  overlap. Implemented in `silverlab/baselines.py` without NumPy.
