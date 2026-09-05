from __future__ import annotations

import json
from pathlib import Path

import pytest

from dpc.parse.text import repair_cp1252_mojibake

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "encoding" / "mojibake.json"

# Real broken values captured from the archive, with their repairs.
CASES = json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "case", CASES, ids=[f"{c['source']}-{i}" for i, c in enumerate(CASES)]
)
def test_repairs_every_captured_case(case):
    assert repair_cp1252_mojibake(case["broken"]) == case["repaired"]


def test_the_fixture_covers_the_characters_that_actually_occur():
    """Dashes and quotes are the bulk of the damage; make sure they are exercised."""
    repaired = " ".join(c["repaired"] for c in CASES)
    for char, name in [
        ("—", "em dash"),
        ("–", "en dash"),
        ("’", "right single quote"),
        ("“", "left double quote"),
        ("”", "right double quote"),
        ("…", "ellipsis"),
    ]:
        assert char in repaired, f"no {name} in the captured cases"


@pytest.mark.parametrize(
    ("broken", "expected"),
    [
        ("Hidden Gem VI \x97 Mid-Term Quiz", "Hidden Gem VI — Mid-Term Quiz"),
        ("Color Slides \x97 A Minimal Challenge", "Color Slides — A Minimal Challenge"),
        ("group shots \x96 just ensure", "group shots – just ensure"),
        ("Churchill\x92s Quandary", "Churchill’s Quandary"),
        ("Baby says; \x93I\x92ve never seen\x94", "Baby says; “I’ve never seen”"),
        ("Self-indulgence\x85 Please", "Self-indulgence… Please"),
    ],
)
def test_named_examples(broken, expected):
    assert repair_cp1252_mojibake(broken) == expected


def test_clean_text_is_untouched():
    for text in ["Free Study 2019-03", "café — already correct", "", "plain ascii"]:
        assert repair_cp1252_mojibake(text) == text


def test_leaves_codepoints_windows_1252_does_not_define():
    # 0x81, 0x8D, 0x90 are undefined in cp1252. Guessing would be worse than
    # leaving them, and there are only a handful in the whole archive.
    for undefined in "\x81\x8d\x90":
        assert repair_cp1252_mojibake(undefined) == undefined


def test_is_idempotent():
    once = repair_cp1252_mojibake("Churchill\x92s Quandary")
    assert repair_cp1252_mojibake(once) == once
