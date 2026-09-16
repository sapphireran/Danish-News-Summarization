# Chunking and length budgets

Every model in this project has a hard context window. The 2023 scripts implement their own packing instead of relying on silent truncation. This note explains the algorithm, the mixed units it uses, and how the GPU-free demo in `examples/text_chunking.py` mirrors it.

## Why packing exists

| Model | Practical window | What happens if you ignore it |
| --- | --- | --- |
| OPUS-MT da↔en | 512 tokens | Tail of the article is dropped; later facts never reach the summarizer |
| T5 news summarizer | 512 tokens | Same, plus the English lead only covers the lead of the *English* text |
| mT5 fine-tune | 1024 input / 128 label | Long bodies are truncated at train time; long silver summaries are clipped |

Translation and English summarization therefore **split then stitch**. Fine-tuning instead **truncates**, which is a different and harsher policy.

## Two units of length

The original helpers mix two notions of length:

1. **Tokenizer token length** — `len(tokenizer.encode(sentence, add_special_tokens=True))`. This is the budget that actually matters for the model.
2. **Whitespace word length** — `split_long_sentence` increments `current_length` by `len(word) + 1` (character length of the word plus a space), then compares that running sum to `text_max_length`, which was computed in *tokens*.

That second comparison is a unit mismatch. It is conservative for Danish (words are often shorter in characters than in SentencePiece tokens) and can over-split dense compounds. The example reimplementation keeps the same mismatch on purpose so demos match the course code. A revival of the pipeline should compare **token** length inside `split_long_sentence` as well.

## Algorithm

### Step A — Sentence tokenize

```
raw_sentences = nltk.sent_tokenize(article)
```

Danish period handling is acceptable for news prose. Abbreviations (`f.eks.`, `bl.a.`, `ca.`) occasionally split too early. The synthetic sample set includes one abbreviation-heavy sentence so the demo can show the break.

### Step B — Oversized sentence split

For each sentence, if `token_len > text_max_length`:

1. Word-tokenize.
2. Grow a chunk.
3. Flush at `,`, `;`, or `:` if the running *character* length is still below the cap.
4. Otherwise flush just before the word that would cross the cap.
5. Re-encode each chunk to store its token length.

Short sentences skip this step.

### Step C — Greedy packing

Walk the `(text, token_len)` list:

- If `current_length + length > text_max_length`, start a new pack.
- Otherwise append.

Packs are lists of strings, not joined text, because `translate()` expects a list (one sentence per batch item). Summarization joins a pack with spaces before calling T5.

### Step D — Downstream join

- Translation: translate each sentence, join with spaces, join packs with spaces.
- Summarization: summarize each joined pack, join pack-summaries with spaces.

There is no cross-pack attention. A person mentioned only in pack 3 will not appear in the summary of pack 1.

## Budgets used in the repo

| Script | `max_length` | Pack budget | Notes |
| --- | --- | --- | --- |
| `translate.py` | 512 | `int(512 * 0.9) = 460` | Safety margin for special tokens / prefixes |
| `summary.py` | 512 | 512 | No 90% margin |
| `translate_back.py` | 512 | 512 in `split_into_sentences` (the helper is passed `max_length`, not `text_max_length`) | Summaries are short |
| `finetune.py` | 1024 / 128 | n/a (truncation) | Labels longer than 128 tokens are cut |
| `eval.py` | 1024 / 128 | n/a | Same as fine-tune |

## Worked numeric example

Suppose `text_max_length = 20` and we have four sentences with token lengths 8, 7, 9, 4.

```
pack 1: [s1, s2]      8 + 7 = 15  (9 would overflow)
pack 2: [s3, s4]      9 + 4 = 13
```

If s3 were 30 tokens, Step B would split it before packing.

The demo script prints this kind of trace with real Danish sample articles and a **whitespace-approximate tokenizer** so you do not need `transformers` installed to study the control flow. Tests in `tests/test_text_chunking.py` lock the greedy rule down with exact counts.

`examples/compare_budgets.py` runs the same article at 16, 40, and 460 to show the character-shredding regime, the sentence-pack regime, and the one-window production regime.

## Approximate tokenizer in the examples

`examples/text_chunking.py` exposes:

```python
class WhitespaceTokenizer:
    def encode(self, text, add_special_tokens=True):
        pieces = text.split()
        extra = 1 if add_special_tokens else 0
        return list(range(len(pieces) + extra))
```

One whitespace word ≈ one token. That is wrong for OPUS-MT SentencePiece (Danish compounds often become several pieces) but good enough to teach packing and to unit-test the algorithm. When you debug a real overflow, always print `len(real_tokenizer.encode(...))`.

## Design implications for summary quality

Because packs are summarized independently:

- Lead-style T5 will emit a *new lead* for the middle of the article. Silver labels therefore contain more mid-article facts than a human news lead would.
- Repetition penalty is per pack, not global. The stitched silver summary can repeat a name or a date.
- Entity consistency across packs is unenforced. "Havneby" in pack 1 and "byen" in pack 2 may become two different cities after da→en→da.

If you rebuild the factory, consider hierarchical summarization: summarize packs, then summarize the concatenation of pack summaries in one extra T5 call. The 2023 code does not do this.

## Relation to mT5's 1024-token body limit

Silver labels can mention facts from pack 4 of a long article. Fine-tuning then truncates the body to 1024 tokens, so the model is asked to generate a fact it can no longer see. That is a hidden source of hallucination. Mitigation options, none of which were implemented in the course scripts:

- Filter training pairs where the silver summary aligns only with the truncated prefix (token-overlap heuristic).
- Raise the fine-tune max length if VRAM allows.
- Generate silver labels from the same 1024-token prefix you will train on.

The sample dataset in `examples/data/` is short enough that this issue does not appear, which is why the walkthrough can stay honest without a GPU.
