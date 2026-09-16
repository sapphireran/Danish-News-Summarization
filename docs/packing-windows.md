# Packing windows

Two functions in `translate.py` disagree about what a "token" is.

## `split_long_sentence`

```
current_length += len(word) + 1
```

This is a **character** budget. It prefers to cut on `,` `;` `:` while
still under `text_max_length`. If a word pushes the running length over
the budget, that word starts the next chunk. Reconstruction is
`' '.join(current_chunk)` after `nltk.word_tokenize`, so punctuation
grows spaces: `Havnen , sagde hun .`

## `split_into_sentences`

```
sentence_length = len(tokenizer.encode(sentence, add_special_tokens=True))
```

This is a **subword** budget from the OPUS tokenizer. Pieces are packed
greedily until the next piece would exceed `text_max_length`.

`text_max_length` is `int(512 * 0.9) == 460` in `translate.py` and
`summary.py`.

## `translate_back.py` is a third variant

* no long-sentence splitter
* `split_into_sentences(article, max_length, tokenizer)` passes **512**,
  not 460, into a parameter named `text_max_length`

So the back-translation hop is allowed slightly larger batches than the
forward hop. Whether that mattered on real summaries (which are short)
is doubtful. It is still a scar.

## Why the study kit uses budget 40

The Vesterklit stories are 6 sentences. A 460-piece budget never
splits them, so the greedy packer would look like a no-op. Examples
use 40 **word** tokens so you can see windows form. That is a
demonstration parameter, not a claim that 2023 used 40.

```bash
python -m fjordpress pack --budget 40 -v
python -m fjordpress counter --text "Direktør Lisbeth Holm sagde, at bølgerne ved Sølvdyp målte over fire meter."
```

`counter` prints three notions on one sentence: word count, char+1, and
a ×1.3 subword guess.
