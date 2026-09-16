# Limitations, leakage, and ethics

Silver-label summarization is a shortcut. This note lists the ways it can lie, leak, or cause harm, so the personal project is not mistaken for a production news system.

## Scientific limitations

### Translationese as supervision

Every training label has passed through English. Danish discourse markers (`jo`, `nemlig`, `efter sigende`), passive bureaucratic style, and quote structure get flattened. mT5 then learns to write slightly English-shaped Danish. Automatic metrics that themselves use multilingual embeddings may not punish this.

### Entity and number drift

da→en and en→da independently hallucinate or drop:

- Place names that collide with common nouns
- Party letter codes (`S`, `V`, `SF`) that English T5 may expand incorrectly
- Kroner amounts, percents, and dates

The fine-tune objective treats the drifted string as truth. The model is rewarded for repeating the factory's mistakes.

### Pack-wise summaries are not leads

Independent T5 calls on 512-token windows produce a collage, not a journalist's lead. Training on collages teaches mT5 to ramble through the article instead of ranking information.

### Truncation vs. label span mismatch

Silver labels can mention facts from the tail of a long article. Fine-tuning truncates bodies to 1024 tokens. The model is then asked to emit facts it cannot see, which encourages hallucination.

### Metric mismatch

`finetune.py` selects the best checkpoint with ROUGE-1 mid-F. That metric likes unigram overlap, including overlap with translationese function words. A more faithful but more abstractive checkpoint can lose the selection race.

### Script-level inconsistency

Eval and qualitative scripts load `small_model` while training saves `large_model`. Reported numbers and trained weights can silently refer to different runs. Always write down the directory you actually scored.

## Data leakage risks

1. **Overlap with Nordjylland News.** If the 10k-article dump included the same stories as the evaluation set, silver-label training is contaminated even if the *labels* differ. Dedup by URL or by high token-overlap before training.
2. **Near-duplicate follow-ups.** Danish local news reprints. Random row splits put the same event on both sides.
3. **Evaluation on silver labels.** Scores become "distance to OPUS-MT+T5," not "distance to a Danish summary."
4. **Trainer `test_dataset` unused.** `finetune.py` loads a test CSV and never evaluates it. People then reuse that file casually and think it is held-out official data.

## Ethical issues

### Copyright and redistribution

The original article dump is not in this repository. Do not commit scraped news. The files under `examples/data/` are original fiction written for documentation; they are not real reporting and must not be cited as news.

### Represented as journalism

A model trained this way can emit confident, fluent Danish that looks like a news lead. Publishing those strings as summaries of real articles without a human editor is misleading. This project is an academic experiment, not an editorial tool.

### People and accusations

News bodies contain names, crimes, and medical details. A hallucinated summary can attach the wrong charge to the wrong person. There is no factuality filter in the 2023 pipeline. Do not run the factory on current crime reporting and post the output.

### Dual use

A cheap "summarize any Danish article" model can be used to mass-produce misleading recaps. The mitigation here is social, not technical: this repo is a documented student project, the examples are synthetic, and the README refuses a production framing.

### Environmental cost

mT5-large for 20 epochs plus two full-corpus translation passes is a non-trivial GPU budget for a course project. The example suite exists so the *ideas* can be inspected without repeating that cost.

### Attribution of labor

Silver labels hide the English T5 author's work and the OPUS-MT bitext authors' work inside a "Danish dataset." If you publish a derived dataset, say that labels are machine-generated via those models.

## What this repository does about it

- Keeps original course scripts (honest historical record) instead of quietly shipping a "safe" rewrite that still looks authoritative.
- Ships only synthetic example articles.
- Documents failure modes next to the happy-path README.
- Separates official eval data from factory outputs in the docs, even when the 2023 scripts are messy.

## What a careful revival should add

None of the following is implemented in the 2023 scripts:

- Named-entity agreement checks between `body` and silver `summary` (drop or flag mismatches).
- Number checksums (compare integers in source and label).
- Dedup against the Nordjylland evaluation documents.
- A human-rated slice (even 50 articles) before quoting automatic metrics.
- A refusal to summarize articles in sensitive categories (crime, health, elections) without review.

Until those exist, treat every generation as **untrusted text**.
