"""Parse a ``challenge_results.php`` page.

That URL serves three genuinely different documents, and the old scraper treated
them as one. It indexed a ten-element list positionally and cached whatever came
back, so a challenge that was merely *unfinished* got parsed into nonsense (or
crashed) and was then cached forever, never to be retried.
"""

from __future__ import annotations

import copy
import re
from datetime import date
from enum import StrEnum

from bs4 import BeautifulSoup

from dpc.parse.text import (
    clean_text,
    collapse_whitespace,
    parse_date,
    parse_int,
    soupify,
    strip_ordinals,
)
from dpc.parse.types import ChallengeRecord

_INVALID_MARKER = "Invalid CHALLENGE_ID"
_RESULTS_PREAMBLE = "Challenge Results for "
_IMAGE_HREF = re.compile(r"/image\.php\?IMAGE_ID=(\d+)")

_DESCRIPTION_STYLE = "display:block; margin-left: 22px; margin-top: -16px;"
_DESCRIPTION_HEADING = "description"
_STATS_STYLE = "margin: 2px;"

_DATE_FORMATS = ("%b %d %Y", "%b. %d %Y", "%B %d %Y")

_DATE_RANGE_PARTS = 2

# Match stats lines by a distinctive keyword in their label rather than by
# position, so a reordered or reworded row fails loudly instead of silently
# landing in the wrong column.
_SUBMISSION_DATES = "submission dates"
_VOTING_DATES = "voting dates"
_FIELD_KEYWORDS = {
    "num_submissions": "submissions",
    "num_disqualifications": "disqualif",
    "num_votes": "votes",
    "num_comments": "comments",
    "average_score": "average",
    "highest_score": "highest",
    "median_score": "median",
    "lowest_score": "lowest",
}


class ChallengePage(StrEnum):
    """Which of the three documents came back."""

    RESULTS = "results"
    """A finished challenge with a results table. Parseable."""

    INVALID = "invalid"
    """No such challenge. Safe to remember permanently and never refetch."""

    UNFINISHED = "unfinished"
    """The challenge exists but is still open, so there are no results yet.

    Must NOT be cached permanently -- it will become a results page later.
    """


class ChallengeNotAvailableError(Exception):
    """Raised when asked to parse a page that carries no results."""

    def __init__(self, kind: ChallengePage) -> None:
        super().__init__(f"challenge page has no results (kind={kind.value})")
        self.kind = kind


def classify(html: str) -> ChallengePage:
    if _INVALID_MARKER in html:
        return ChallengePage.INVALID
    if _RESULTS_PREAMBLE in html:
        return ChallengePage.RESULTS
    return ChallengePage.UNFINISHED


def parse_challenge(html: str, challenge_id: int) -> ChallengeRecord:
    """Parse a finished challenge's results page.

    Raises:
        ChallengeNotAvailableError: the page is an invalid-id or unfinished page.
        ValueError: the page looks like results but the stats block did not match.
    """
    kind = classify(html)
    if kind is not ChallengePage.RESULTS:
        raise ChallengeNotAvailableError(kind)

    soup = soupify(html)

    heading = soup.find("tr", {"class": "forum-heading"})
    name = clean_text(heading)
    if not name.startswith(_RESULTS_PREAMBLE):
        msg = f"challenge {challenge_id}: unexpected heading {name!r}"
        raise ValueError(msg)
    name = name[len(_RESULTS_PREAMBLE) :].strip()

    description = _description(soup)

    fields = _stats_fields(soup, challenge_id)
    submission_start, submission_end = _date_range(fields, _SUBMISSION_DATES, challenge_id)
    voting_start, voting_end = _date_range(fields, _VOTING_DATES, challenge_id)

    def number(field: str) -> str:
        return _lookup(fields, _FIELD_KEYWORDS[field], challenge_id, field)

    return ChallengeRecord(
        id=challenge_id,
        name=name,
        description=description,
        submission_start=submission_start,
        submission_end=submission_end,
        voting_start=voting_start,
        voting_end=voting_end,
        num_submissions=parse_int(number("num_submissions")),
        num_disqualifications=parse_int(number("num_disqualifications")),
        num_votes=parse_int(number("num_votes")),
        num_comments=parse_int(number("num_comments")),
        average_score=float(number("average_score")),
        highest_score=float(number("highest_score")),
        median_score=float(number("median_score")),
        lowest_score=float(number("lowest_score")),
    )


def parse_image_ids(html: str) -> tuple[int, ...]:
    """Image ids linked from a challenge page, de-duplicated, order preserved.

    The old builder emitted duplicates into the site data and relied on a
    ``uniq`` in the Hugo template to hide them.
    """
    soup = soupify(html)
    seen: dict[int, None] = {}
    for link in soup.find_all("a", {"class": "i"}):
        match = _IMAGE_HREF.search(str(link.get("href", "")))
        if match:
            seen.setdefault(int(match.group(1)), None)
    return tuple(seen)


def _description(soup: BeautifulSoup) -> str:
    """The challenge blurb, without the bold "Description" heading above it."""
    node = soup.find("div", {"style": _DESCRIPTION_STYLE})
    if node is None:
        return ""

    node = copy.copy(node)
    heading = node.find("b")
    if heading is not None and clean_text(heading).rstrip(":").lower() == _DESCRIPTION_HEADING:
        heading.decompose()
    return collapse_whitespace(node)


def _stats_fields(soup: BeautifulSoup, challenge_id: int) -> dict[str, str]:
    """Split the stats block into ``{lowercased label: value}``."""
    node = soup.find("div", {"style": _STATS_STYLE})
    if node is None:
        msg = f"challenge {challenge_id}: no stats block (style={_STATS_STYLE!r})"
        raise ValueError(msg)

    fields: dict[str, str] = {}
    for line in clean_text(node).splitlines():
        stripped = collapse_whitespace(line)
        if ":" not in stripped:
            continue
        label, _, value = stripped.partition(":")
        fields[label.strip().lower()] = value.strip()

    if not fields:
        msg = f"challenge {challenge_id}: stats block had no 'label: value' lines"
        raise ValueError(msg)
    return fields


def _lookup(fields: dict[str, str], keyword: str, challenge_id: int, field: str) -> str:
    for label, value in fields.items():
        if keyword in label:
            return value
    msg = (
        f"challenge {challenge_id}: no stats label matching {keyword!r} for {field}; "
        f"labels present: {sorted(fields)}"
    )
    raise ValueError(msg)


def _date_range(fields: dict[str, str], keyword: str, challenge_id: int) -> tuple[date, date]:
    raw = _lookup(fields, keyword, challenge_id, keyword)
    parts = [strip_ordinals(part).strip() for part in raw.split(" - ")]
    if len(parts) != _DATE_RANGE_PARTS:
        msg = f"challenge {challenge_id}: {keyword} is not a range: {raw!r}"
        raise ValueError(msg)
    return (
        parse_date(parts[0], *_DATE_FORMATS),
        parse_date(parts[1], *_DATE_FORMATS),
    )
