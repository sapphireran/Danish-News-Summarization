"""CLI smoke tests for python -m pakhus."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pakhus", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_scars_cli() -> None:
    proc = _run(["scars"])
    assert proc.returncode == 0, proc.stderr
    assert "converter-only-en-da" in proc.stdout
    assert "summary-ten-row-slice" in proc.stdout


def test_list_cli() -> None:
    proc = _run(["list"])
    assert proc.returncode == 0
    assert "tof-001" in proc.stdout
    assert "tof-010" in proc.stdout


def test_atlas_cli() -> None:
    proc = _run(["atlas", "--article", "tof-001"])
    assert proc.returncode == 0
    assert "pane 00" in proc.stdout
    assert "hop 2" in proc.stdout.lower() or "hop 2" in proc.stdout


def test_pack_back_scar() -> None:
    proc = _run(["pack", "--article", "tof-010", "--packer", "course_back"])
    assert proc.returncode == 0
    assert "EMPTY" in proc.stdout
    assert "OVER" in proc.stdout
