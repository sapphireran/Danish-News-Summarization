"""Scar scanner must still see the frozen 2023 mismatches."""

from __future__ import annotations

from pakhus.scars import SCARS, scan_repo
from pakhus.paths import COURSE_SCRIPTS, course_script


def test_all_course_scripts_exist() -> None:
    for name in COURSE_SCRIPTS:
        assert course_script(name).is_file()


def test_every_scar_present() -> None:
    report = scan_repo()
    assert report.missing == [], [s.scar_id for s in report.missing]
    assert len(report.present) == len(SCARS)


def test_assignments_include_model_paths() -> None:
    report = scan_repo()
    translate = report.assignments["translate.py"]
    assert translate.get("model_path") == "models/opus-mt-da-en_ct2"
    converter = course_script("Ctranslate_converter.py").read_text(encoding="utf-8")
    assert "opus-mt-en-da" in converter
    assert converter.count("TransformersConverter") >= 1
