# Ablation protocol (if I retrain)

I am not retraining mT5 in this branch. If I do it later, I want the
comparisons decided in advance so I cannot shop for a table.

## Frozen pieces

- Tokenizer and generation cap used at eval (`max_length=128`, `num_beams`
  documented per run).
- Nordjylland split and column remap, written down in the run JSON.
- The fiction lab, which is **not** an ablation — it is a smoke test that
  the code still runs.

## Things worth turning off, one at a time

| Knob | 2023 default | Why ablate |
| --- | --- | --- |
| da→en model | `opus-mt-da-en` via CT2 | NLLB was already in comments |
| English teacher | `mrm8488/t5-base-finetuned-summarize-news` | A lead-2 English teacher is the obvious control |
| en→da model | `opus-mt-en-da` via CT2 | Same as the forward hop |
| Packing budget | 90% of 512 tokens, character-flavoured | Token-only packing may keep more ledes |
| Student size | `mt5-large` in `finetune.py` | `mt5-small` is what eval already names |
| Epochs | 20 | Early-stop on a real val silver split |
| Optimizer | Adafactor, lr `3e-4`, polynomial, warmup 1000 | One run with AdamW at a lower lr |
| FP16 | on | mT5 + fp16 was a 2023-era gamble |
| Label smoothing / dropout | dropout 0.1 in config | Did it do anything? |

## Controls that are not optional

1. **Lead-2 student.** Train nothing. Score lead-2 Danish on Nordjylland.
   If I cannot beat it on faithfulness, I stop.
2. **English-teacher ceiling.** Translate Nordjylland to English, summarize,
   translate back, score. That number is the hop's own identity. The student
   cannot honestly claim to beat a teacher I never measured.
3. **No-hop student.** Fine-tune mT5 on Nordjylland train (with a leakage
   note) so I know what "real pairs" look like on the same metric code.
4. **Error-sheet subsample.** 50 silver labels tagged with the catalog
   codes. Report `NUM`+`ENT` rate, not just ROUGE.

## Logging

Each run writes one JSON next to the checkpoint:

```json
{
  "date": "YYYY-MM-DD",
  "git": "sha",
  "teacher": "…",
  "student": "…",
  "packing": {"max_length": 512, "ratio": 0.9},
  "nordjylland": {"rouge1_f": null, "bertscore_f1": null},
  "hop_ceiling": {"rouge1_f": null},
  "notes": "no invented numbers in the template"
}
```

`notes/run-log-template.md` is not in this branch on purpose. I do not want
a second empty template competing with the one on the docs-only PR. The
schema above is enough.

## What I will not call an ablation

- Changing the fiction briefs.
- Tweaking the HTML report CSS.
- Editing `summary.py`'s `[:10]` without also running the full hop.
