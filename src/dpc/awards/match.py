"""Deciding whether a comment grants an award. Pure, and therefore testable."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from dpc.awards.catalog import AwardDefinition
from dpc.parse.text import soupify

_QUOTE_TABLE: dict[str, Any] = {"align": "center", "width": "95%"}
"""dpchallenge renders a quoted comment as a centred 95%-width table.

This selector was written into the original parser and then commented out, so
quotes were never actually removed.
"""

_QUOTE_HINT = "95%"
"""Cheap pre-check: matching runs over every comment an awarder ever wrote, and
almost none of them contain a quote, so avoid parsing HTML unless one might."""


def strip_quotes(raw_comment: str) -> str:
    """Remove quoted blocks from a comment's HTML.

    Replying to an award and quoting it copies the award's image into the reply,
    which would otherwise read as the award being given a second time. Three of
    the four duplicate grants in the archive are exactly that -- see
    https://www.dpchallenge.com/image.php?IMAGE_ID=1160121, where the awarder
    quotes their own earlier award two days later.

    Only the matcher does this. ``raw_comment`` keeps the full original markup,
    because the comment corpus is worth preserving intact.
    """
    if _QUOTE_HINT not in raw_comment:
        return raw_comment

    soup = soupify(raw_comment)
    quotes = soup.find_all("table", _QUOTE_TABLE)
    if not quotes:
        return raw_comment

    for quote in quotes:
        quote.decompose()
    return str(soup)


def matches(raw_comment: str, award: AwardDefinition) -> bool:
    """True when the comment's own HTML carries any of the award's markers.

    Matching runs against the markup rather than the extracted text, because the
    markers are image and anchor URLs that text extraction discards -- and
    against the comment minus anything it quotes, so that quoting an award does
    not award it again.
    """
    body = strip_quotes(raw_comment)
    return any(marker in body for marker in award.markers)


def awards_in(raw_comment: str, candidates: Iterable[AwardDefinition]) -> list[AwardDefinition]:
    """Every award whose markers appear in this comment, in catalogue order."""
    body = strip_quotes(raw_comment)
    return [award for award in candidates if any(m in body for m in award.markers)]
