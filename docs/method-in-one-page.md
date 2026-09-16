# Method in one page

ITU ANLP 2023 final: Danish abstractive summarization without starting from human Danish labels.

## Ingredients

| Piece | Choice | Why then |
| --- | --- | --- |
| Unlabeled source | ~10k Danish news articles (local CSV, not in git) | Course-sized, already on disk |
| Pivot language | English | Strong off-the-shelf news summarizer |
| DA↔EN | Helsinki OPUS-MT, converted with CTranslate2 | Small enough to batch on one GPU |
| Summarizer | `mrm8488/t5-base-finetuned-summarize-news` | Already news-domain, not generic T5 |
| Student model | `google/mt5-large` | Had seen Danish in pretraining |
| Exam set | Nordjylland News (human TV2 Nord summaries) | Public, Danish, same domain-ish |

## Algorithm

1. Convert Marian checkpoints to CTranslate2.
2. Translate each Danish article to English, packing under ~460 tokens.
3. Summarize each English pack with T5 (`max_length=80`, `repetition_penalty=5.0`).
4. Translate each English summary back to Danish.
5. Split the silver CSV by hand into train/val/test.
6. Fine-tune mT5 20 epochs, select on silver-val ROUGE-1 mid F.
7. Look at Nordjylland generations; compute ROUGE + Danish BERTScore.

## What I claim

- The *pipeline* is specified by the scripts plus [`script-contracts.md`](script-contracts.md).
- The *method* is ordinary translate–summarize–translate silver labeling.

## What I do not claim

- A numeric improvement over a Danish-only baseline. No table landed in git.
- That silver labels match journalist style. Hop 3 is Marian, not TV2 Nord.
- That a clean clone reproduces 2023 training. See the blockers in the contract sheet.

## What the 2026 examples claim

Only that the **shapes** (columns, packer control flow, hop order) can be exercised on fictional rows with the standard library. See [`examples-guide.md`](examples-guide.md).
