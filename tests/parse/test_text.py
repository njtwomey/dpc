from __future__ import annotations

from datetime import date

import pytest

from dpc.parse.text import (
    collapse_whitespace,
    parse_date,
    parse_int,
    strip_ordinals,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Jan. 1st 2004", "Jan. 1 2004"),
        ("Jan. 2nd 2004", "Jan. 2 2004"),
        ("Jan. 3rd 2004", "Jan. 3 2004"),
        ("Jan. 4th 2004", "Jan. 4 2004"),
        ("Dec. 31st 2024", "Dec. 31 2024"),
        ("Jan. 22nd 2004", "Jan. 22 2004"),
    ],
)
def test_strip_ordinals_handles_every_suffix(raw, expected):
    assert strip_ordinals(raw) == expected


def test_strip_ordinals_leaves_non_ordinals_alone():
    # The old code did date[1][:-2], which would happily maul any token.
    assert strip_ordinals("August 2004") == "August 2004"
    assert strip_ordinals("Free Study 2019-03") == "Free Study 2019-03"


def test_parse_int_accepts_thousands_separators():
    assert parse_int("12,345") == 12345
    assert parse_int(" 678 ") == 678


def test_parse_date_tries_each_format():
    assert parse_date("Jan 1 2004", "%b %d %Y", "%b. %d %Y") == date(2004, 1, 1)
    assert parse_date("Jan. 1 2004", "%b %d %Y", "%b. %d %Y") == date(2004, 1, 1)


def test_parse_date_reports_what_it_could_not_parse():
    with pytest.raises(ValueError, match="could not parse"):
        parse_date("not a date", "%b %d %Y")


def test_collapse_whitespace_flattens_newlines_and_nbsp():
    assert collapse_whitespace("a\n  b\xa0 c ") == "a b c"
