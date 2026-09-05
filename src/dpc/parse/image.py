"""Parse an ``image.php`` page: the vote breakdown, the stats, and the comments."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup, Tag

from dpc.parse.text import clean_text, parse_datetime, soupify
from dpc.parse.types import VOTE_BUCKETS, CommentRecord, ImageRecord, ImageStats

_STATS_HEADING = "Statistics"
"""Current markup: a table headed "Statistics" holding <b>Label:</b> value rows."""

_LEGACY_START = '<td>Voting Breakdown <span style="font-weight: normal;">'
_LEGACY_END = '<td valign="top" width="450" class="textsm">'
"""The panel dpchallenge served until it was redesigned. Pages cached before
then still parse, and the ten-bucket vote histogram only exists there -- the
current site does not publish it at all."""

_LABEL = re.compile(r"<b>\s*([^<:]+?)\s*:\s*</b>\s*([^<]*)")

_DISQUALIFIED_MARKER = "avg (all users)"
_DURING_CHALLENGE_MARKER = "Comments Made During the Challenge"
_EDITED_MARKER = "Message edited by author "

_USER_ID = re.compile(r"USER_ID=(\d+)")
_COMMENT_TABLE: dict[str, Any] = {
    "width": "90%",
    "cellspacing": "1",
    "cellpadding": "2",
    "align": "center",
}

_COMMENT_DATE_FORMATS = ("%m/%d/%Y %I:%M:%S %p",)
_EDITED_DATE_FORMATS = ("%Y-%m-%d %H:%M:%S",)

# Accept thousands separators. The old pattern was ([\d\.]+), which stopped at
# the first comma -- so "Views since voting: 1,234" was silently recorded as 1.
_NUMBER = r"([\d,]+(?:\.\d+)?)"

_COMMENTER_LINK_INDEX = 2
"""The third anchor in a comment header row links to the commenter."""


class ImageStatsUnavailableError(Exception):
    """The page carried no statistics panel in any known markup.

    Distinct from a disqualified image, which *has* the panel but no averages.
    Confusing the two would mark the entire archive disqualified, so a missing
    panel is raised rather than guessed at -- it means the page is an error page
    or the markup has changed again.

    The old parser split on the panel's marker and indexed ``[1]``, so this case
    raised a bare IndexError that ``get_challenge`` swallowed with
    ``print(f"Failed with {link=}")``.
    """


def parse_image(html: str, image_id: int, challenge_id: int) -> ImageRecord:
    soup = soupify(html)

    title = clean_text(soup.find("div", {"class": "imagetitle"}))

    # The first a.u carrying a USER_ID, rather than a fixed position among them.
    # The page also renders ruleset and portfolio links with the same class, and
    # their order has changed before -- picking by position silently attributes
    # an image to whoever happens to sit in that slot.
    photographer_id = None
    for link in soup.find_all("a", {"class": "u"}):
        found = _USER_ID.search(str(link.get("href", "")))
        if found:
            photographer_id = int(found.group(1))
            break
    if photographer_id is None:
        msg = f"image {image_id}: no link carrying a USER_ID"
        raise ValueError(msg)

    return ImageRecord(
        id=image_id,
        challenge_id=challenge_id,
        photographer_id=photographer_id,
        name=title,
        stats=parse_image_stats(html, soup),
    )


def parse_image_stats(html: str, soup: BeautifulSoup | None = None) -> ImageStats:
    """Parse the voting breakdown panel.

    A disqualified image keeps its vote histogram and view count but loses every
    average and its finishing place, so those come back as ``None``.
    """
    soup = soup if soup is not None else soupify(html)
    section = _stats_section(html, soup)
    if section is None:
        msg = "no statistics panel on the page in any known markup"
        raise ImageStatsUnavailableError(msg)

    fields = {label.strip().lower(): value.strip() for label, value in _LABEL.findall(section)}

    # The histogram exists only in the pre-redesign markup; the current site
    # does not publish per-score counts, so this is empty for new scrapes.
    # Averages remain public -- no login needed for any of this.
    votes = tuple(
        int(clean_text(el)) for el in soup.find_all("div", {"class": "breakdown_vote_count"})
    )
    if votes and len(votes) != VOTE_BUCKETS:
        msg = f"expected {VOTE_BUCKETS} vote buckets, found {len(votes)}"
        raise ValueError(msg)

    views = _int(fields, "views since voting")

    # A disqualified image keeps its view count but loses every average and its
    # finishing place. Judged inside the panel, never by the panel's absence.
    if _DISQUALIFIED_MARKER not in fields:
        return ImageStats(votes=votes, disqualified=True, num_views=views)

    return ImageStats(
        votes=votes,
        disqualified=False,
        position=_int(fields, "place"),
        average_all=_float(fields, "avg (all users)"),
        # Dropped in the redesign; still present on pages cached before it.
        average_commenters=_float(fields, "avg (commenters)"),
        average_participants=_float(fields, "avg (participants)"),
        average_non_participants=_float(fields, "avg (non-participants)"),
        num_views=views,
        num_votes=_int(fields, "votes"),
    )


def parse_comments(
    html: str, image_id: int, soup: BeautifulSoup | None = None
) -> list[CommentRecord]:
    """Parse every comment on an image page, in document order.

    Comments are laid out as a flat run of ``<td>`` cells in groups of three
    (anchor + author, timestamp, body), with a divider row marking where
    during-challenge comments begin.
    """
    soup = soup if soup is not None else soupify(html)
    table = soup.find("table", _COMMENT_TABLE)
    if table is None:
        return []

    comments: list[CommentRecord] = []
    during_challenge = False
    rows = iter(table.find_all("td"))

    for row in rows:
        if clean_text(row) == _DURING_CHALLENGE_MARKER:
            during_challenge = True

        anchor = row.find("a")
        if anchor is None or "name" not in anchor.attrs:
            continue

        links = row.find_all("a")
        if len(links) <= _COMMENTER_LINK_INDEX:
            continue
        commenter_link = links[_COMMENTER_LINK_INDEX]
        user_match = _USER_ID.search(str(commenter_link.get("href", "")))
        if user_match is None:
            continue

        timestamp_cell = next(rows, None)
        body_cell = next(rows, None)
        if timestamp_cell is None or body_cell is None:
            break

        body_text = clean_text(body_cell)
        body_text, edited = _split_edited(body_text)

        comments.append(
            CommentRecord(
                id=int(str(anchor.attrs["name"])),
                image_id=image_id,
                commenter_id=int(user_match.group(1)),
                commenter_name=clean_text(commenter_link),
                raw_comment=_inner_html(body_cell),
                comment=body_text,
                date=parse_datetime(clean_text(timestamp_cell), *_COMMENT_DATE_FORMATS),
                edited=edited,
                made_during_challenge=during_challenge,
            )
        )

    return comments


def _split_edited(text: str) -> tuple[str, datetime | None]:
    """Separate a trailing 'Message edited by author <timestamp>.' marker."""
    head, marker, tail = text.rpartition(_EDITED_MARKER)
    if not marker:
        return text, None
    return head.strip(), parse_datetime(tail.strip()[:19], *_EDITED_DATE_FORMATS)


def _inner_html(cell: Tag) -> str:
    """The comment body as HTML.

    Award matching runs against this, because award markers are image and anchor
    URLs that do not survive text extraction.
    """
    inner = cell.find("td")
    return str(inner if inner is not None else cell)


def _stats_section(html: str, soup: BeautifulSoup) -> str | None:
    """The statistics panel's HTML, in whichever markup the page uses."""
    for heading in soup.find_all("tr", {"class": "forum-heading"}):
        if clean_text(heading) == _STATS_HEADING:
            table = heading.find_parent("table")
            if table is not None:
                return str(table)

    _, marker, rest = html.partition(_LEGACY_START)
    if marker:
        section, _, _ = rest.partition(_LEGACY_END)
        return section

    return None


def _raw_number(fields: dict[str, str], label: str) -> str | None:
    """The leading number of a field, e.g. "1 out of 40" -> "1"."""
    value = fields.get(label)
    if value is None:
        return None
    match = re.search(_NUMBER, value)
    return None if match is None else match.group(1).replace(",", "")


def _int(fields: dict[str, str], label: str) -> int | None:
    raw = _raw_number(fields, label)
    # Some counts render as "7.0"; int() will not take that directly.
    return None if raw is None else int(float(raw))


def _float(fields: dict[str, str], label: str) -> float | None:
    raw = _raw_number(fields, label)
    return None if raw is None else float(raw)
