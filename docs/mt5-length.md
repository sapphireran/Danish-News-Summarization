# mT5 length knobs against Danish almanac prose

`finetune.py` as committed:

| Knob | Value | Why it shows up on measures |
| --- | --- | --- |
| input truncate | 1024 | A packed OPUS window is 460 pieces; 1024 is comfortable for one article |
| label truncate | 128 | Silver lines in this lab are 12–25 words. 128 is not the bottleneck |
| `min_length` | 9 | Stops empty generations; does not restore a dropped number |
| `max_length` / `generation_max_length` | 128 | Same |
| `length_penalty` | 0.8 | Slightly prefers shorter strings — bad for keeping `2,4 mg/l` *and* `50 mg/l` |
| `no_repeat_ngram_size` | 3 | Can block a repeated amount (`47,2 mm` … `47,2 mm`) |
| `num_beams` | 4 | Fine |
| `dropout_rate` | 0.1 | Fine |
| epochs | 20 | Easy to memorize sixteen rows; the real 10k dump is a different story |
| lr | 3e-4, polynomial, 1000 warmup | As committed |
| optim | Adafactor, weight decay 0.01 | As committed |
| batch | 8, no grad accum | Needs a 2023-class GPU for `mt5-large` |
| `fp16` | True | As committed |
| best model | `rouge_1_mid_fmeasure` | Rewards n-gram overlap, not `2,4` vs `24` |

`eval.py` loads `google/mt5-small` tokenizer with a `small_model` body
and a 64-row eval batch. `use_model.py` generates with `num_beams=2`,
`no_repeat_ngram_size=1` (harsher than training), `max_length=128`.

None of those knobs parse a decimal comma. A model can score a decent
ROUGE-1 on `bh-02` while emitting `24 ha` instead of `2,4 ha`, because
`ha` and `vårbyg` still overlap. That is why the ledger exists.
