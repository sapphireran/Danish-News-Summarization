"""Run the documentation demos and a few self-checks.

    python examples/run_all_demos.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.data.corpus import ARTICLES
from examples.danish_sentences import sent_tokenize
from examples.length_filter import FilterThresholds, decide
from examples.rouge_lite import rouge_n, rouge_scores
from examples.text_chunking import SimpleWordTokenizer, split_article, split_long_sentence


def _run(script: str, extra: list[str] | None = None) -> None:
    command = [sys.executable, "-u", str(ROOT / "examples" / script), *(extra or [])]
    print("\n" + "#" * 72, flush=True)
    print("$", " ".join(command), flush=True)
    print("#" * 72, flush=True)
    subprocess.run(command, check=True, cwd=ROOT)


def self_check() -> None:
    print("self-check: sentence splitter keeps Danish abbreviations together")
    text = "Kommunen åbner kl. 11 og 14. Der er gratis omvisning."
    sentences = sent_tokenize(text)
    assert sentences == [
        "Kommunen åbner kl. 11 og 14.",
        "Der er gratis omvisning.",
    ], sentences

    print("self-check: long-sentence split honors comma boundaries")
    long = "Første del, anden del, tredje del og en hale der bliver ved."
    chunks = split_long_sentence(long, max_length=20)
    assert len(chunks) >= 2, chunks
    assert all(chunk.strip() for chunk in chunks), chunks

    print("self-check: packing a long article yields more than one window")
    tokenizer = SimpleWordTokenizer()
    long_body = next(article["danish_body"] for article in ARTICLES if article["id"] == "da-008")
    windows = split_article(long_body, text_max_length=40, tokenizer=tokenizer)
    assert len(windows) >= 2, windows
    for window in windows:
        assert len(tokenizer.encode(window)) <= 40 + 5, (
            "window exceeded budget by more than a leftover long token"
        )

    print("self-check: identical strings get perfect ROUGE-1")
    p, r, f1 = rouge_n("den røde kutter", "den røde kutter", n=1)
    assert (p, r, f1) == (1.0, 1.0, 1.0), (p, r, f1)

    print("self-check: disjoint strings get zero ROUGE-2")
    scores = rouge_scores("abc def", "xyz uvw")
    assert scores.rouge2_f1 == 0.0

    print("self-check: corpus has 10 articles and a 6/2/2 split")
    assert len(ARTICLES) == 10
    counts = {"train": 0, "validation": 0, "test": 0}
    for article in ARTICLES:
        counts[article["split"]] += 1
    assert counts == {"train": 6, "validation": 2, "test": 2}, counts

    print("self-check: default length filter drops the short museum note")
    museum = next(article for article in ARTICLES if article["id"] == "da-005")
    decision = decide(
        museum["id"],
        museum["danish_body"],
        museum["danish_summary"],
        FilterThresholds(),
    )
    assert decision.keep is False, decision
    print("self-check: passed")


def main() -> None:
    print("running example self-checks", flush=True)
    self_check()
    _run("data/write_tables.py")
    _run("validate_schemas.py")
    _run("inspect_dataset.py", ["--preview", "1"])
    _run("run_chunking_demo.py", ["--max-length", "80"])
    _run("run_silver_label_walkthrough.py", ["--id", "da-001"])
    _run("run_rouge_demo.py")
    _run("compare_summaries.py", ["--id", "da-005"])
    _run("length_filter.py")
    _run("report_hyperparameters.py")
    print("\nall demos finished", flush=True)


if __name__ == "__main__":
    main()
