# Personal retrospective (ITU ANLP/DL, December 2023)

Written 16 September 2026. I am not reconstructing a lost report from memory and calling it data. I am writing down the course-project decisions that are still visible in the Python, and the opinions I still hold.

## What the course project was for

I needed a final project that was:

- clearly NLP + deep learning (not a toy classifier)
- finishable on one GPU weekend plus a few evenings
- about a language I care about (Danish) without pretending I had a new annotated corpus
- mine — a personal repo under `sapphireran` / `pang990801`, not a workplace artifact

The sentence I would have put on a slide:

> Automatically label Danish news by pivoting through an English summarizer, then fine-tune mT5 and see what Nordjylland ROUGE says.

That is a *systems* project with a *measurement* attached. In 2023 I under-built the measurement. In 2026 I am documenting both halves so I cannot gaslight myself.

## What I think worked

**The pipeline shape is honest.** Three hops, files on disk between hops, CSVs I could open in a spreadsheet when the GPU job looked drunk. That is the right granularity for a course: I can blame a hop.

**CTranslate2 was the correct engineering call.** Hugging Face generate on 10k articles × N sentences would have been the whole budget. Marian in CTranslate2 is the reason a pivot corpus was thinkable.

**Keeping gold out of training was the interesting constraint.** Anyone can fine-tune mT5 on Nordjylland train and report a number. I wanted the awkward setup: train on a machine-made style, test on a human blurb style. That is closer to “I have crawl, I do not have editors.”

**ROUGE-1 as a checkpoint rule was conventional, not clever.** I knew that. I still think it is acceptable for *selection among my own runs*, as long as I do not advertise it as meaning “best summarizer.”

## What I think failed

**I shipped eval scripts that cannot be trusted to load the model I trained.** `large_model` vs `small_model`, mT5-large vs mT5-small, `text` vs `input_text`. That is not a research limitation. That is unfinished homework. See [docs/known-issues.md](../docs/known-issues.md).

**I left NLLB DNA in the OPUS scripts.** I can still see the moment I changed my mind (commented converters, leftover `dan_Latn`). I did not finish the refactor. Every silver label may be slightly wrong in the same way, which is the worst kind of bug: systematic and invisible in a fluent CSV.

**I did not freeze the world.** No `requirements.txt` in 2023, no dataset revision, no seed, no `run.json`. The 2026 `requirements.txt` is an apology note, not time travel.

**I evaluated with the wrong emotional target.** I wanted a number that would look like the papers. The honest deliverable was a 20-row error analysis and a paragraph on label shift. DanSum already warned that ROUGE and BERTScore miss factual errors. I cited that mentally and then optimized ROUGE-1 anyway.

**`use_model.py` lied to me about which article I was reading.** Batch index vs dataset index. Any “the model said X about story Y” memory from those prints is suspect.

## What I would tell 2023-me on 15 December

1. Pick OPUS *or* NLLB. Delete the other path.
2. Write `split_dataset.py` before `finetune.py`.
3. Save tokenizer + `git rev-parse HEAD` + `pip freeze` into the model directory.
4. Make `eval.py` import generate kwargs from one dict.
5. Print five raw Nordjylland rows before you write `remove_columns`.
6. Remove `[:10]` the same hour you add it, or put it behind `if os.getenv("SMOKE")`.
7. Do not spend the last night on 20 epochs. Spend it on a baseline and a rubric.

None of that required a new idea. It required treating the repo like I would treat a personal tool I had to rerun in a year. I am doing that now.

## Relation to later public Danish / Nordic eval

ScandEval grew up into a broader European eval story (EuroEval). Their summarization headline is no longer “ROUGE-1 mid F from a Trainer hook.” If I reran in 2026 for curiosity, I would still keep ROUGE + BERTScore for continuity with 2023, and I would add chrF++ and a language check so I can talk to current Nordic eval practice.

I would still **not** submit this pivot model to a public leaderboard. The training labels are a different task.

## Ethics / sourcing (personal)

The 10k file name says `articles_without_linebreaks`. I do not document a scrape recipe here and I will not add one. News text is not “free because I can download it.” Nordjylland on the Hub is CC0 and cited. The unlabeled dump is the part I would be most careful with if I ever rebuilt the corpus.

Generated summaries can invent accidents, charges, and names. A course demo is one thing. I would not put this model behind a “Danish news summary” button without a human.

## Why this documentation pass exists

I wanted a personal, substantial write-up of what this repo actually is: a 2023 lab dump with a clear idea and uneven measurement. Expanding docs does not make the missing scores appear. It does make the next personal experiment cheaper.

If I only have time for one more artifact after this, it should be a single `eval` script that loads `./large_model` correctly and writes `notes/runs/<date>.md`. Not another model scale-up.
