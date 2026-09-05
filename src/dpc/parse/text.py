"""Shared text and date helpers for the parsers."""

from __future__ import annotations

import re
from datetime import date, datetime

from bs4 import BeautifulSoup, Tag

_ORDINAL = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)\b", re.IGNORECASE)


def _cp1252_c1_map() -> dict[int, str]:
    """Map C1 control codepoints to the windows-1252 characters they stand for.

    Bytes 0x80-0x9F are printable in windows-1252 (curly quotes, dashes, the
    ellipsis) but control characters in latin-1. Text decoded with the wrong one
    ends up holding the control character instead. A few of those bytes are
    genuinely undefined in windows-1252; they are left alone rather than guessed.
    """
    table: dict[int, str] = {}
    for code in range(0x80, 0xA0):
        try:
            table[code] = bytes([code]).decode("cp1252")
        except UnicodeDecodeError:
            continue
    return table


CP1252_C1 = _cp1252_c1_map()
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


def repair_cp1252_mojibake(text: str) -> str:
    """Undo windows-1252 text that was decoded as latin-1.

    ``Hidden Gem VI \x97 Mid-Term Quiz`` becomes ``Hidden Gem VI — Mid-Term Quiz``.

    For rows scraped before the fetch layer decoded correctly. New scrapes come
    through clean, so this is only ever applied to historical data. Text without
    C1 characters is returned unchanged.
    """
    return text.translate(CP1252_C1)
