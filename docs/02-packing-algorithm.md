# Packing algorithm (2023 reconstruction)

This is a prose reconstruction of the helpers in `translate.py` and
`summary.py`. The CPU lab in `pakhus/packing.py` follows the same control
flow so a fixture can be packed both *as the course did* and *with
consistent units*.

## Long-sentence saw

`split_long_sentence(sentence, max_length)` does **not** count tokenizer
ids. It word-tokenizes, then accumulates `len(word) + 1` (the character
length plus a space) until that running sum reaches `max_length`.

Split policy:

- If the current word is `,`, `;`, or `:` **and** the running character
  sum is still *below* the budget, flush the chunk at that punctuation.
  The punctuation is kept at the end of the finished chunk.
- If the running sum meets or passes the budget, pop the last word, flush,
  and start a new chunk with the popped word.
- Flush any remainder at the end.

The join is `' '.join(current_chunk)`. NLTK-style tokenization peels
punctuation into its own token, so the reconstructed text contains spaces
before commas: `havnen , derefter kajen`. That spacing is part of the
silver-label distribution the 2023 run would have fed to mT5.

`max_length` here is `text_max_length` from the caller (460 in
`translate.py`, 512 in `summary.py`). It is a token budget being used as
a character budget. On Danish news prose that is roughly a **4× too
small** saw: 460 characters is about 70–90 words, while 460 OPUS tokens
is several hundred words.

## Sentence list packer

After each raw sentence is optionally sawn, the file builds
`(text, encoded_length)` pairs using `tokenizer.encode(...,
add_special_tokens=True)`. Those pairs are packed with:

```
if current_length + length > budget:
    emit current_list
    current_list = [sentence]
    current_length = length
else:
    append and add
```

Consequences that the lab tests for:

1. A first sentence that is already over budget (possible in
   `translate_back.py`, which never saws) emits an **empty list** before
   the singleton, because `current_list` starts empty and the `>` branch
   still appends it.
2. Chunks produced by the character saw are **not re-checked** against
   the token budget. An over-long singleton window is allowed. The model
   truncates later.
3. There is no overlap between adjacent windows. Coreference that
   straddles the cut is gone.

## Detokenized windows vs model input

`translate.py` then calls `translate(sentences)` on each list: every
sentence in the window is encoded separately and passed to
`translator.translate_batch`. The window budget therefore limits the
*sum* of per-sentence encodings, not one concatenated sequence. Special
tokens are counted once per sentence, so a window of many short sentences
is more expensive than the same words as one sentence.

`summary.py` goes the other way. It joins each packed list back into a
single string (`sentences_to_text`) and encodes that string as **one** T5
sequence of up to 512 tokens. The two hops do not mean the same thing by
"window".

## The two packers in this repo

| Function | Matches | Length for the saw | Length for packing | Empty-list guard |
| --- | --- | --- | --- | --- |
| `pakhus.packing.pack_course_translate` | `translate.py` | characters | approx. encoder ids | no |
| `pakhus.packing.pack_course_summary` | `summary.py` | characters | approx. encoder ids | no |
| `pakhus.packing.pack_course_back` | `translate_back.py` | none | approx. encoder ids, budget 512 | no |
| `pakhus.packing.pack_consistent` | personal baseline | same unit | same unit | yes, drop empties, resplit overs |

The "approx. encoder" in the CPU lab is not SentencePiece. It is a
deterministic stand-in documented in `pakhus/tokenize.py`, close enough
to show fragmentation and leftover panes. It is not a claim about OPUS
token counts.
