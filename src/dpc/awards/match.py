"""Deciding whether a comment grants an award. Pure, and therefore testable."""

from __future__ import annotations

from collections.abc import Iterable

from dpc.awards.catalog import AwardDefinition


def matches(raw_comment: str, award: AwardDefinition) -> bool:
    """True when the comment's HTML carries any of the award's markers.

    Matching runs against the raw HTML, not the extracted text, because the
    markers are image and anchor URLs that text extraction discards.
    """
    return any(marker in raw_comment for marker in award.markers)


def awards_in(raw_comment: str, candidates: Iterable[AwardDefinition]) -> list[AwardDefinition]:
    """Every award whose markers appear in this comment, in catalogue order."""
    return [award for award in candidates if matches(raw_comment, award)]
