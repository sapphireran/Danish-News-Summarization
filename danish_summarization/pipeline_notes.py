"""Static notes about the original course scripts.

The examples print these notes so a later reader can see what each root
script expects without opening every file at once.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StageNote:
    script: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    models: tuple[str, ...]
    summary: str
    caveats: tuple[str, ...]


STAGES: tuple[StageNote, ...] = (
    StageNote(
        script="Ctranslate_converter.py",
        inputs=(),
        outputs=("models/opus-mt-en-da_ct2",),
        models=("Helsinki-NLP/opus-mt-en-da",),
        summary=(
            "Converts the English-to-Danish OPUS-MT checkpoint to CTranslate2. "
            "The Danish-to-English converter is present but commented out."
        ),
        caveats=(
            "translate.py loads models/opus-mt-da-en_ct2, so the da-en block "
            "in this script must be uncommented before the forward pass.",
            "NLLB conversion paths are commented out leftovers from earlier trials.",
        ),
    ),
    StageNote(
        script="translate.py",
        inputs=("10000_articles_without_linebreaks.csv",),
        outputs=("translated_articles.csv",),
        models=("models/opus-mt-da-en_ct2", "Helsinki-NLP/opus-mt-da-en"),
        summary=(
            "Reads Danish article bodies, packs sentences into 512-token windows, "
            "and writes English translations beside the original Danish text."
        ),
        caveats=(
            "Expects a column named 'article text', not 'body'.",
            "Passes NLLB-style language prefixes (dan_Latn / eng_Latn) into OPUS-MT.",
        ),
    ),
    StageNote(
        script="summary.py",
        inputs=("translated_articles.csv",),
        outputs=("summarized_file_ml80_rp5.0.csv",),
        models=("mrm8488/t5-base-finetuned-summarize-news",),
        summary=(
            "Summarizes each English translation with an English news T5 model. "
            "Long articles are split, summarized in pieces, then concatenated."
        ),
        caveats=(
            "The published script slices the frame to the first 10 rows.",
            "Generation uses max_length=80 and repetition_penalty=5.0.",
        ),
    ),
    StageNote(
        script="translate_back.py",
        inputs=("summarized_file_ml80_rp5.0.csv",),
        outputs=("labeled_dataset_ml80_rp5.0.csv",),
        models=("models/opus-mt-en-da_ct2", "Helsinki-NLP/opus-mt-en-da"),
        summary=(
            "Translates English summaries back to Danish to produce silver labels "
            "paired with the original Danish bodies."
        ),
        caveats=(
            "Drops the English translation and English summary columns from the export.",
            "Sentence packing uses max_length rather than the 0.9 safety budget.",
        ),
    ),
    StageNote(
        script="finetune.py",
        inputs=(
            "datasets/train_dataset.csv",
            "datasets/validation_dataset.csv",
            "datasets/test_dataset.csv",
        ),
        outputs=("./large_model", "mt5-summarize-large"),
        models=("google/mt5-large",),
        summary=(
            "Fine-tunes mT5-large on Danish body/summary pairs with ROUGE-1 as "
            "the checkpoint metric."
        ),
        caveats=(
            "fp16=True can be unstable on mT5 depending on the GPU and Transformers version.",
            "datasets.load_metric('rouge') is the older datasets API.",
        ),
    ),
    StageNote(
        script="use_model.py",
        inputs=("ScandEval/nordjylland-news-summarization-mini",),
        outputs=(),
        models=("small_model", "google/mt5-small"),
        summary=(
            "Prints a handful of generated summaries next to gold summaries from "
            "the Nordjylland mini split."
        ),
        caveats=(
            "Loads google/mt5-small tokenizer but weights from ./small_model.",
            "Inspection loop prints input_text[i] while decoding batch i, so a "
            "batch size of 2 only lines up for the first item in each batch.",
        ),
    ),
    StageNote(
        script="eval.py",
        inputs=("alexandrainst/nordjylland-news-summarization",),
        outputs=(),
        models=("small_model", "google/mt5-small"),
        summary=(
            "Runs ROUGE and Danish BERTScore on the full Nordjylland news test split."
        ),
        caveats=(
            "Uses datasets.load_metric rather than the evaluate package that is imported.",
            "BERTScore requests xlm-roberta-large, which is a large extra download.",
        ),
    ),
)


def format_stage(note: StageNote) -> str:
    """Render one stage as a plain-text block for CLI examples."""
    lines = [
        f"script:    {note.script}",
        f"summary:   {note.summary}",
    ]
    if note.inputs:
        lines.append("inputs:    " + ", ".join(note.inputs))
    if note.outputs:
        lines.append("outputs:   " + ", ".join(note.outputs))
    if note.models:
        lines.append("models:    " + ", ".join(note.models))
    if note.caveats:
        lines.append("caveats:")
        for caveat in note.caveats:
            lines.append(f"  - {caveat}")
    return "\n".join(lines)


def format_all_stages() -> str:
    """Render every stage, separated by blank lines."""
    return "\n\n".join(format_stage(note) for note in STAGES)
