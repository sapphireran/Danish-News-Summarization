# Course report (reconstructed, 2026)

ITU *Advanced Natural Language Processing and Deep Learning*, autumn 2023.
This is not the PDF I submitted. The PDF is gone from the repo. What follows
is the argument I still stand behind, written so a later clone can see the
method without the missing CSVs or checkpoints.

## Abstract

Danish abstractive summarization is data-poor if you insist on human
article–summary pairs. The 2023 project built a **silver** training set by
pivoting through English: translate a Danish news article, summarize it with a
news-tuned English T5, translate the summary back. An mT5 student was then
fine-tuned on the resulting Danish pairs. The interesting claim is not that
the student is strong. The interesting claim is that **the teacher is a
pipeline**, and every hop can write a fact that no Danish editor would sign.

This archive still has the seven course scripts. It does not have the 10k
source dump, the CTranslate2 directories, the train/val/test CSVs, or a
metric printout. I will not invent a ROUGE table to fill that hole. The
personal lab under `silverlab/` is the control experiment I should have run
first: extractive baselines and a typed error sheet on original fiction.

## 1. Problem

News summarization for Danish has a public pair set
([Nordjylland News](nordjylland.md)) built from TV2 Nord. That set is useful
for **evaluation**. It is the wrong shape to pretend that "just fine-tune
mT5" is a complete project: the course wanted a story about *creating*
supervision when you only have raw articles.

The raw articles I used in 2023 never entered git. Treat
`10000_articles_without_linebreaks.csv` as a local artifact with a documented
header (`id`, `article text`), not as something a stranger can download from
this repository.

## 2. Method

```
Danish article
    │  OPUS-MT da→en  (CTranslate2)
    ▼
English article
    │  mrm8488/t5-base-finetuned-summarize-news
    ▼
English summary
    │  OPUS-MT en→da  (CTranslate2)
    ▼
Danish silver summary
    │  google/mt5-large  (Seq2SeqTrainer, 20 epochs, Adafactor)
    ▼
Danish student
```

Sentence packing is the unglamorous core. Both translation scripts and the
English teacher split long copy so a 512-piece encoder does not silently
truncate the lede. The 2023 splitters mix **character** budgets with
**tokenizer** lengths. That quirk is left in the course scripts; the lab
reimplements packing only as sentence splitting plus extractive selection.

## 3. Why English is a loaded teacher

`mrm8488/t5-base-finetuned-summarize-news` is a competent English news
summarizer. It is also a model of **English news style**: agency leads,
Western entity priors, a habit of rounding numbers. Pivoting through it is
not a free lunch. See [danish-language.md](danish-language.md) and
[error-catalog.md](error-catalog.md).

Back-translation as data augmentation (Sennrich et al., 2016) was designed
for bitext, where the target side is already trusted. Here the target side
is born in the pipeline. That is closer to cross-lingual summarization
(WikiLingua, NCLS) than to classical BT.

## 4. Experiments that actually exist in git

| Artifact | In git? | What a clone can do |
| --- | --- | --- |
| Course scripts | yes | Read them. Running them needs weights + dump + GPU. |
| 10k Danish dump | no | Nothing honest. Do not scrape a stand-in. |
| Silver CSVs | no | Use `examples/data/fiction_briefs.json` instead. |
| `large_model` / `small_model` | no | `use_model.py` and `eval.py` will not load. |
| 2023 ROUGE / BERTScore | no | Do not quote a number. |
| Fiction lab | this branch | `python3 -m silverlab metrics` |

`eval.py` scores a local `small_model` on
`alexandrainst/nordjylland-news-summarization` with ROUGE and Danish
BERTScore (`xlm-roberta-large`). `finetune.py` writes `./large_model` and
selects checkpoints by `rouge_1_mid_fmeasure`. Those filenames already
disagree. That is a [script scar](script-scars.md), not a result.

## 5. What I now treat as the real finding

The pipeline is a **fact factory**. A Saturn/Saturday swap, an 80→18 collapse,
or a unit promotion from metres to kilometres will be trained as if a Danish
desk wrote them. Automatic metrics on Nordjylland will not reliably punish
that, because the public summaries were written under a different newsroom
contract than the silver labels.

The lab's job is to make that claim inspectable: extractive ceilings on
honest gold, a rubric with named axes, and a catalog of hop errors that are
anchored in text I actually wrote.

## 6. What I would still change

1. Run lead-2 and TextRank **before** spending a conversion night on OPUS-MT.
2. Keep a 50-article human sheet with the [rubric](annotation-rubric.md).
3. Freeze a metric JSON next to each checkpoint.
4. Evaluate the English teacher on a translated Nordjylland slice so the hop
   has a number of its own.
5. Stop prefixing OPUS-MT with NLLB language tokens.

None of that is retroactively sitting in the 2023 scripts. It lives here as
notes and as code that runs on a laptop.
