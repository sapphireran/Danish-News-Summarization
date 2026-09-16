# Limitations and ethics

This project manufactures supervision. That is a valid course experiment. It is a weak basis for publishing "state of the art Danish summarization" numbers without a human study.

## Silver labels are not gold

Each training target is the composition of:

1. Marian Danish→English error
2. T5-base news hallucination / omission
3. Marian English→Danish error
4. Chunk-and-join discourse artifacts
5. 128-token truncation at fine-tune time

mT5 will imitate that composition, including fluent-looking factual errors. ROUGE against the same teacher will look optimistic.

## Translationese and register

Back-translated Danish often:

- keeps English word order
- picks a near-calque (`tage sted` vs. a more idiomatic verb)
- loses modal particles (`jo`, `nok`, `vel`) that a Danish journalist would use
- normalizes named entities incorrectly (people, ministries, town spellings)

A model trained only on that register will sound like translated English news even when it is "correct."

## Domain and people

The 2023 source dump was Danish news. News summarization systems are routinely used to:

- compress coverage of accidents, crime, and politics
- surface a lede that may omit a denied allegation or a later correction
- amplify a mistaken number (vote shares, casualties, prices)

Automatic labels make those failure modes harder to audit because there is no journalist to compare against on the train set. Nordjylland eval catches *some* of this, not all.

Do not deploy these weights to write headlines, notifications, or push summaries without a human editor.

## Dual-use and scraping

- This repo does **not** include the 10k-article dump. Do not add copyrighted news archives to git.
- The `examples/data/*.csv` rows are fictional municipal sketches written for this documentation. They are not real reporting.
- If you rebuild a corpus, respect the site's terms, robots rules, and any research license on Nordjylland / ScandEval.

## Biases inherited from the teacher stack

| Component | Known issues that transfer |
| --- | --- |
| OPUS-MT da-en / en-da | Gender stereotypes, weak handling of rare names, code-switching |
| English news T5 | US/UK news priors, majority-entity focus, number hallucination |
| mT5 / mC4 | Web-crawl toxicity and representation gaps for minority Danish varieties |
| XLM-R BERTScore | Rewards overlap with the reference's framing, not "fairness" |

## Evaluation gaps

- No factual consistency metric (e.g. NLI alignment, QAFactEval) in `eval.py`.
- No human side-by-side.
- `use_model.py` print alignment is off after the first batch (see [06-evaluation.md](06-evaluation.md)).
- Silver test ROUGE is not reported by any script.

## Privacy

News text can contain names of private individuals. The original dump is not redistributed here. Do not commit real article CSVs, trainer logs that print full bodies, or Hub pushes of models trained on unlicensed text without checking the license.

## License of *this* repo

MIT for the code and the original example/documentation text. Upstream model and dataset licenses are separate:

- Helsinki-NLP OPUS-MT: check the model card (typically CC-BY / research use — verify before commercial use)
- `mrm8488/t5-base-finetuned-summarize-news`: derived from T5 + news data; see that card
- `google/mt5-*`: see the mT5 card and mC4
- Nordjylland / ScandEval: see the dataset cards

## If you only remember one thing

Treat `labeled_dataset_*.csv` as a **distillation target**, not as truth. Report teacher-fidelity and human-set transfer as different questions.
