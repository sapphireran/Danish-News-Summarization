# Glossary

| Term | Meaning in this repo |
| --- | --- |
| **Abstractive summary** | A lede that may rephrase the article instead of copying a sentence. The English T5 and mT5 stages are abstractive in intent; chunk concatenation makes many silver labels feel extractive. |
| **Adafactor** | Optimizer used in `finetune.py`. Lower memory than Adam because it factored second-moment estimates; the default T5 / mT5 fine-tune choice. |
| **BERTScore** | Embedding-based overlap metric. Here: XLM-RoBERTa large, `lang='da'`. |
| **CTranslate2** | Fast inference runtime for Transformer MT. `Ctranslate_converter.py` writes a CT2 directory that `ctranslate2.Translator` loads. |
| **Lede** | The short opening summary of a news article. Nordjylland-News targets are typically one-sentence ledes. |
| **mT5** | Multilingual T5 (`google/mt5-*`). The model actually fine-tuned for Danish summarization. |
| **Marian / OPUS-MT** | Bilingual MT checkpoints from Helsinki-NLP. `opus-mt-da-en` and `opus-mt-en-da` are the pivot translators. |
| **NLLB** | Meta’s many-to-many MT model. Commented out in the converter. Its `dan_Latn` / `eng_Latn` codes still appear in the OPUS scripts. |
| **Nordjylland-News** | Danish TV2 Nord article–summary set (Alexandra Institute; also packaged by ScandEval). Evaluation only. |
| **Pivot language** | English as an intermediate: DA→EN→summarize→EN→DA. |
| **ROUGE** | Recall-oriented n-gram overlap with a reference. This repo reports mid F-measure for ROUGE-1/2/L. |
| **ROUGE mid** | The median of bootstrap confidence-interval estimates from `rouge-score` (`value.mid.fmeasure`), not a custom statistic. |
| **Silver label** | A training target produced by a model (here: translate–summarize–translate) rather than a human. |
| **Window / pack** | Greedy packing of consecutive sentences into a token budget so a 512-token model can see a long article in pieces. |
| **mC4** | The multilingual C4 crawl mT5 was pretrained on. Includes Danish, which is why mT5 can be fine-tuned without a Danish-only LM. |

## File-name fragments

| Fragment | Source |
| --- | --- |
| `ml80` | English summary `max_length=80` |
| `rp5.0` | English summary `repetition_penalty=5.0` |
| `ct2` | CTranslate2 converted directory |
| `without_linebreaks` | the unlabeled dump is expected as one article per CSV row, no raw `\n` in the body |
