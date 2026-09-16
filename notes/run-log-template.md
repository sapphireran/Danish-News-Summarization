# Run log template

Copy to `notes/runs/YYYY-MM-DD-<slug>.md` when a personal rerun produces numbers. Do not fill this template with invented scores.

## Identity

- Date:
- Machine (GPU, VRAM, CUDA):
- Git SHA:
- Python / `pip freeze` file:
- Hugging Face dataset revision (Nordjylland):
- Hugging Face dataset revision (mini, if used):

## Data

- Source CSV name and row count:
- `summary.py` slice removed? (yes/no)
- Silver split script + seed + ratios:
- Train / val / silver-test counts:
- Overlap check vs Nordjylland test (method + hit count):

## Hops

- DA→EN model + CT2 compute type:
- NLLB-style prefixes used? (yes/no)
- EN summarizer + generate kwargs:
- EN→DA model:
- Spot-check: 3 raw triples (DA, EN, silver DA) attached below or not:

## Train

- Student init:
- Epochs / lr / schedule / batch / accum / fp16:
- `metric_for_best_model` + best epoch:
- Tokenizer saved next to weights? (yes/no)
- Weights path:

## Decode (must match eval)

- beams / max_length / min_length / length_penalty / no_repeat_ngram_size:

## Automatic scores

| Split | N | ROUGE-1 | ROUGE-2 | ROUGE-L | BERTScore F1 | chrF++ | mean pred chars | empty | not_da |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| silver test |  |  |  |  |  |  |  |  |  |
| Nordjylland test |  |  |  |  |  |  |  |  |  |
| lead-N baseline |  |  |  |  |  |  |  |  |  |
| unfinetuned mT5 |  |  |  |  |  |  |  |  |  |

## Human sheet

- N rated:
- LANG fail count:
- HAL yes count:
- mean ENT / COV:
- notes:

## Decision

- Keep / mix with gold / retire pivot:
- Next change (one sentence):
