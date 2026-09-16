# Bibliography

Personal reading list for the notes in this folder. Links are public.

## Models and methods

- Raffel, Colin, et al. 2020. "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer." *JMLR*. ([T5](https://arxiv.org/abs/1910.10683))
- Xue, Linting, et al. 2021. "mT5: A Massively Multilingual Pre-trained Text-to-Text Transformer." *NAACL*. ([mT5](https://arxiv.org/abs/2010.11934))
- Tiedemann, Jörg, and Santhosh Thottingal. 2020. "OPUS-MT — Building open translation services for the World." *EAMT*.
- NLLB Team. 2022. "No Language Left Behind: Scaling Human-Centered Machine Translation." ([NLLB](https://arxiv.org/abs/2207.04672))
- Sennrich, Rico, Barry Haddow, and Alexandra Birch. 2016. "Improving Neural Machine Translation Models with Monolingual Data." *ACL*.
- See, Abigail, Peter J. Liu, and Christopher D. Manning. 2017. "Get To The Point: Summarization with Pointer-Generator Networks." *ACL*.
- Lewis, Mike, et al. 2020. "BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension." *ACL*.
- Zhang, Jingqing, et al. 2020. "PEGASUS: Pre-training with Extracted Gap-sentences for Abstractive Summarization." *ICML*.
- Mihalcea, Rada, and Paul Tarau. 2004. "TextRank: Bringing Order into Text." *EMNLP*.

## Evaluation

- Lin, Chin-Yew. 2004. "ROUGE: A Package for Automatic Evaluation of Summaries." *ACL Workshop*.
- Zhang, Tianyi, et al. 2020. "BERTScore: Evaluating Text Generation with BERT." *ICLR*.

## Danish / Nordic data

- Kinch, Oliver. *Nordjylland News Summarization*. Alexandra Institute. Dataset card: [alexandrainst/nordjylland-news-summarization](https://huggingface.co/datasets/alexandrainst/nordjylland-news-summarization). CC0. TV2 Nord source.
- ScandEval harness and the Nordjylland mini split used by `use_model.py`.
- CTranslate2 documentation for the converter in `Ctranslate_converter.py`.

## English teacher checkpoint

- `mrm8488/t5-base-finetuned-summarize-news` on the Hugging Face Hub — the
  teacher loaded by `summary.py`. I am using it as a historical artifact of
  the 2023 script, not as an endorsement.
