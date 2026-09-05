"""Shared text and date helpers for the parsers."""

from __future__ import annotations

import re
from datetime import date, datetime

from bs4 import BeautifulSoup, Tag

_ORDINAL = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)\b", re.IGNORECASE)
_WHITESPACE = re.compile(r"\s+")

HTML_PARSER = "lxml"


def soupify(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, HTML_PARSER)


def clean_text(value: Tag | str | None) -> str:
    """Normalise a node or string to plain text with tidy whitespace."""
    if value is None:
        return ""
    text = value.get_text() if isinstance(value, Tag) else value
    return text.replace("\xa0", " ").strip()


def collapse_whitespace(value: Tag | str | None) -> str:
    """Like :func:`clean_text` but also collapses runs of whitespace to one space."""
    return _WHITESPACE.sub(" ", clean_text(value)).strip()


def strip_ordinals(value: str) -> str:
    """``Jan. 1st 2004`` -> ``Jan. 1 2004``.

    The old code did ``date[1] = date[1][:-2]``, which happened to work only
    because every English ordinal suffix is two characters -- and would silently
    corrupt any token that was not an ordinal at all.
    """
    return _ORDINAL.sub(r"\1", value)


def parse_int(value: str) -> int:
    """Parse an integer that may carry thousands separators."""
    return int(value.replace(",", "").strip())


def parse_date(value: str, *fmt: str) -> date:
    """Parse a date, trying each format in turn."""
    return _parse_datetime(value, *fmt).date()


def parse_datetime(value: str, *fmt: str) -> datetime:
    """Parse a naive local timestamp.

    dpchallenge renders timestamps in site-local time with no zone marker, so
    there is nothing truthful to attach. They are stored naive and compared
    only against each other.
    """
    return _parse_datetime(value, *fmt)


def _parse_datetime(value: str, *fmt: str) -> datetime:
    cleaned = collapse_whitespace(value)
    for candidate in fmt:
        try:
            return datetime.strptime(cleaned, candidate)  # noqa: DTZ007 - see docstring
        except ValueError:
            continue
    msg = f"could not parse {cleaned!r} with any of {fmt}"
    raise ValueError(msg)
