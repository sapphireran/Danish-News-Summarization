# Why windows dominate this project

The 2023 scripts never summarize a Danish article in one shot.

Every sequence model in the cascade has a hard length. Helsinki OPUS-MT
was trained around 512 SentencePiece tokens. The English news T5
(`mrm8488/t5-base-finetuned-summarize-news`) is also a 512-token encoder.
mT5-large in `finetune.py` truncates article bodies to 1024 tokens and
labels to 128.

Danish municipal news is often longer than one OPUS window. A 1,200-word
harbour story will not fit. The course code therefore:

1. Splits the article into sentences.
2. Packs sentences into lists whose encoded length stays under a budget.
3. Runs the model on each list.
4. Concatenates the outputs with a space.

That packing house is the actual system. The choice of OPUS vs NLLB, or
mT5-small vs mT5-large, sits on top of it. If the crates are the wrong
size, or if they are emptied and rebuilt between docks, the silver labels
move even when the translators are perfect.

## The three budgets that matter

| Site | File | Budget | Unit the file *claims* | Unit the long-split actually uses |
| --- | --- | --- | --- | --- |
| Danish → English | `translate.py` | `int(512 * 0.9)` = 460 | tokenizer ids | `len(word) + 1` characters inside `split_long_sentence` |
| English → summary | `summary.py` | 512 | T5 tokenizer ids | same mixed character split for long sentences |
| English summary → Danish | `translate_back.py` | 512 passed into the splitter, while `text_max_length` is 460 and unused | tokenizer ids | long sentences are **not** split at all |

Two properties follow.

**Over-fragmentation of long sentences.** A 200-word Danish sentence is
well under 460 OPUS tokens, but it is far over 460 *characters*. The
course splitter therefore saws it at commas after roughly a tweet's worth
of text. The translator never sees the whole clause.

**Under-splitting on the way back.** `translate_back.py` has no
`split_long_sentence`. A glued multi-pane English summary can be shoved
into a singleton window that exceeds 512 tokens and then gets truncated
inside CTranslate2.

## What a window is not

A window is not a paragraph, a journalistic *manchet*, or a 5W slot. It
is an accumulator: sentences are appended until the next one would exceed
the budget. The last pane of a long article is almost always short. The
first pane almost always contains the lede.

That length skew is not cosmetic. The English news T5 is lead-biased. A
full 512-token first pane produces an 80-token summary that sounds like a
news brief. A 90-token leftover pane produces another 80-token summary
that often restates names because there is nothing else in the crate.
`summary.py` then joins them. Silver labels for long articles therefore
contain a sharp lede plus one or more faint echoes.

Pakhuset exists to make those crates visible without downloading the 2023
weights.
