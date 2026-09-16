"""Read the frozen 2023 scripts and report scars that are still present.

The scanner is intentionally picky. If a future edit "fixes" a course file
in place, tests fail so the docs can be updated on purpose instead of
drifting.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass

from pakhus.paths import COURSE_SCRIPTS, course_script


@dataclass(frozen=True)
class Scar:
    scar_id: str
    script: str
    needle: str
    how: str  # "substring" | "regex" | "ast-assign"
    assign_name: str = ""
    description: str = ""


SCARS: tuple[Scar, ...] = (
    Scar(
        "converter-only-en-da",
        "Ctranslate_converter.py",
        "Helsinki-NLP/opus-mt-en-da",
        "substring",
        description="Active converter exports opus-mt-en-da only.",
    ),
    Scar(
        "converter-da-en-commented",
        "Ctranslate_converter.py",
        '# opus_da_en_model = TransformersConverter("Helsinki-NLP/opus-mt-da-en")',
        "substring",
        description="da-en conversion is commented out.",
    ),
    Scar(
        "translate-loads-da-en",
        "translate.py",
        'model_path = "models/opus-mt-da-en_ct2"',
        "substring",
        description="Hop 1 loads a CT2 path the converter does not write.",
    ),
    Scar(
        "nllb-prefix-da-en",
        "translate.py",
        "target_prefixes = [[tgt_lang]",
        "substring",
        description="NLLB-style target_prefix on OPUS-MT.",
    ),
    Scar(
        "nllb-lang-da",
        "translate.py",
        "dan_Latn",
        "substring",
        description="NLLB language tag dan_Latn in an OPUS script.",
    ),
    Scar(
        "nllb-lang-en",
        "translate.py",
        "eng_Latn",
        "substring",
        description="NLLB language tag eng_Latn in an OPUS script.",
    ),
    Scar(
        "decode-drop-first-token",
        "translate.py",
        "result.hypotheses[0][1:]",
        "substring",
        description="Drops the first hypothesis token, matching NLLB forced lang.",
    ),
    Scar(
        "summary-ten-row-slice",
        "summary.py",
        "[:10]",
        "substring",
        description="Silver labelling is sliced to ten rows.",
    ),
    Scar(
        "summary-rep-penalty",
        "summary.py",
        "repetition_penalty=5.0",
        "substring",
        description="Extreme T5 repetition penalty at labelling time.",
    ),
    Scar(
        "summary-max-length-80",
        "summary.py",
        "max_length=80",
        "substring",
        description="Per-pane English summary cap of 80 tokens.",
    ),
    Scar(
        "back-unused-text-max",
        "translate_back.py",
        "text_max_length = int(max_length * 0.9)",
        "substring",
        description="460-token budget is computed and then not passed to the splitter.",
    ),
    Scar(
        "back-splitter-gets-512",
        "translate_back.py",
        "split_into_sentences(article, max_length, tokenizer)",
        "substring",
        description="Back-translation packer receives 512, not text_max_length.",
    ),
    Scar(
        "finetune-mt5-large",
        "finetune.py",
        "google/mt5-large",
        "substring",
        description="Training checkpoint is mT5-large.",
    ),
    Scar(
        "finetune-label-128",
        "finetune.py",
        'mt5_tokenizer(data["summary"], truncation=True, max_length=128)',
        "substring",
        description="Silver labels truncated to 128 tokens at train time.",
    ),
    Scar(
        "finetune-body-1024",
        "finetune.py",
        'mt5_tokenizer(data["body"], truncation=True, max_length=1024)',
        "substring",
        description="Danish bodies truncated to 1024 tokens at train time.",
    ),
    Scar(
        "finetune-fp16",
        "finetune.py",
        "fp16 = True",
        "substring",
        description="fp16 on mT5; NaNs were a known 2023-era issue.",
    ),
    Scar(
        "use-model-small-tokenizer",
        "use_model.py",
        "google/mt5-small",
        "substring",
        description="Demo tokenizer is mT5-small, not the training large.",
    ),
    Scar(
        "use-model-small-weights",
        "use_model.py",
        'local_model_path = "small_model"',
        "substring",
        description="Demo weights path does not match ./large_model.",
    ),
    Scar(
        "use-model-no-repeat-1",
        "use_model.py",
        "no_repeat_ngram_size=1",
        "substring",
        description="Forbids repeating any token, including Danish function words.",
    ),
    Scar(
        "eval-small-weights",
        "eval.py",
        'from_pretrained("small_model")',
        "substring",
        description="eval.py loads small_model, not ./large_model.",
    ),
    Scar(
        "eval-public-dataset",
        "eval.py",
        "alexandrainst/nordjylland-news-summarization",
        "substring",
        description="eval split is public Nordjylland, not the silver CSV.",
    ),
    Scar(
        "use-model-minidataset",
        "use_model.py",
        "ScandEval/nordjylland-news-summarization-mini",
        "substring",
        description="Demo split is a different Nordjylland-mini source than eval.py.",
    ),
    Scar(
        "deprecated-use-auth-token",
        "translate.py",
        "use_auth_token=False",
        "substring",
        description="transformers now wants token=; this will warn or fail.",
    ),
    Scar(
        "deprecated-load-metric",
        "eval.py",
        'datasets.load_metric("rouge")',
        "substring",
        description="datasets.load_metric moved to the evaluate package.",
    ),
)


@dataclass
class ScarReport:
    present: list[Scar]
    missing: list[Scar]
    assignments: dict[str, dict[str, object]]

    @property
    def ok(self) -> bool:
        return not self.missing

    def render(self) -> str:
        lines = ["# 2023 script scars", ""]
        if self.missing:
            lines.append("MISSING (course file changed?):")
            for scar in self.missing:
                lines.append(f"- {scar.scar_id}  {scar.script}: {scar.description}")
            lines.append("")
        lines.append(f"present {len(self.present)} / {len(SCARS)}")
        lines.append("")
        for scar in self.present:
            lines.append(f"- [{scar.script}] {scar.scar_id}")
            lines.append(f"    {scar.description}")
        if self.assignments:
            lines.append("")
            lines.append("# literal assignments")
            for script, mapping in sorted(self.assignments.items()):
                lines.append(f"## {script}")
                for name, value in mapping.items():
                    lines.append(f"    {name} = {value!r}")
        return "\n".join(lines) + "\n"


def _read(script: str) -> str:
    return course_script(script).read_text(encoding="utf-8")


def _literal_assignments(source: str) -> dict[str, object]:
    tree = ast.parse(source)
    out: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                out[target.id] = node.value.value
    return out


def scan_repo() -> ScarReport:
    present: list[Scar] = []
    missing: list[Scar] = []
    assignments: dict[str, dict[str, object]] = {}
    sources = {name: _read(name) for name in COURSE_SCRIPTS}
    for name, source in sources.items():
        assignments[name] = _literal_assignments(source)
    for scar in SCARS:
        text = sources[scar.script]
        found = False
        if scar.how == "substring":
            found = scar.needle in text
        elif scar.how == "regex":
            found = re.search(scar.needle, text) is not None
        elif scar.how == "ast-assign":
            found = assignments[scar.script].get(scar.assign_name) == scar.needle
        (present if found else missing).append(scar)
    return ScarReport(present=present, missing=missing, assignments=assignments)


def assert_course_scripts_frozen() -> None:
    report = scan_repo()
    if report.missing:
        ids = ", ".join(s.scar_id for s in report.missing)
        raise AssertionError(f"expected 2023 scars missing: {ids}")
