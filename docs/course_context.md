# Course context

Repository title: **Danish-News-Summarization**

The original README describes this as the final project for
**ITU Advanced Natural Language Processing and Deep Learning (2023)**:
a Danish summarization model whose training labels are produced
automatically rather than written by hand.

That framing explains several repository choices:

- Almost all of the code is a **data-generation pipeline**, not a
  custom nn.Module. The “model work” is a stock `Seq2SeqTrainer` on
  mT5.
- Evaluation is on a **public Danish news benchmark**
  (Nordjylland-News / ScandEval) so the silver labels are not scored
  against themselves.
- The README is a six-step command list. These docs expand that list
  into contracts and caveats; they do not replace a graded report.

## Related public work (not this repo)

These papers and datasets are the backdrop, not dependencies of the
course scripts:

- **DanSumT5** (Kolding, Nymann, Hansen, Enevoldsen, Kristensen-McLachlan;
  NoDaLiDa 2023) fine-tunes mT5 on a cleaned abstractive subset of
  DaNewsroom and reports ROUGE plus BERTScore plus human rankings.
  Code and models: [Danish-summarisation/DanSum](https://github.com/Danish-summarisation/DanSum).
- **DaNewsroom** (Varab and Schluter, 2020) is the larger Danish
  newsroom summarization collection DanSumT5 filters.
- **Nordjylland-News** (Kinch / Alexandra Institute, 2023) is the TV2
  Nord pair set used here for evaluation and by ScandEval’s
  abstractive-summarization task.
- **ScandEval** (Nielsen, 2023) packages that task as
  `input_text` / `target_text` among other Scandinavian benchmarks.
- **mT5** (Xue et al., 2021) is the pretrained backbone.

This personal repository is an independent course implementation of
*silver-label pivot summarization*, not a fork of DanSum.

## What belongs in git

Safe to commit:

- the seven original scripts
- these docs
- the fictional `examples/data/*` tables
- requirements and `.gitignore`

Keep out of git:

- scraped or licensed news dumps
- converted `models/*_ct2` directories
- `small_model` / `large_model` weights
- trainer `mt5-summarize-*` runs
- any verbatim Nordjylland-News article text

The example corpus is original fiction in a North Jutland local-news
register. It exists so the pipeline can be taught without republishing
newspaper copy.
