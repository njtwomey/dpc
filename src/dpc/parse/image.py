"""Parse an ``image.php`` page: the vote breakdown, the stats, and the comments."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup, Tag

from dpc.parse.text import clean_text, parse_datetime, soupify
from dpc.parse.types import VOTE_BUCKETS, CommentRecord, ImageRecord, ImageStats

_BREAKDOWN_START = '<td>Voting Breakdown <span style="font-weight: normal;">'
_BREAKDOWN_END = '<td valign="top" width="450" class="textsm">'

_DISQUALIFIED_MARKER = "Avg (all users)"
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

_PHOTOGRAPHER_LINK_INDEX = 1
"""The second ``a.u`` on the page is the photographer; the first is the viewer."""

_COMMENTER_LINK_INDEX = 2
"""The third anchor in a comment header row links to the commenter."""


class ImageStatsUnavailableError(Exception):
    """The page carried no voting-breakdown panel at all.

    That panel is only served to a logged-in session, so an anonymous fetch
    produces a page that is otherwise complete but has no scores. It must not be
    confused with a disqualified image, which *has* the panel but no averages --
    reading one as the other would mark the entire archive disqualified.

    The old parser split on the panel's marker and indexed ``[1]``, so this case
    raised a bare IndexError that ``get_challenge`` swallowed with
    ``print(f"Failed with {link=}")``.
    """


def parse_image(html: str, image_id: int, challenge_id: int) -> ImageRecord:
    soup = soupify(html)

    title = clean_text(soup.find("div", {"class": "imagetitle"}))

    user_links = soup.find_all("a", {"class": "u"})
    if len(user_links) <= _PHOTOGRAPHER_LINK_INDEX:
        msg = f"image {image_id}: could not find the photographer link"
        raise ValueError(msg)
    match = _USER_ID.search(str(user_links[_PHOTOGRAPHER_LINK_INDEX].get("href", "")))
    if match is None:
        msg = f"image {image_id}: photographer link carried no USER_ID"
        raise ValueError(msg)

    return ImageRecord(
        id=image_id,
        challenge_id=challenge_id,
        photographer_id=int(match.group(1)),
        name=title,
        stats=parse_image_stats(html, soup),
    )


def parse_image_stats(html: str, soup: BeautifulSoup | None = None) -> ImageStats:
    """Parse the voting breakdown panel.

    A disqualified image keeps its vote histogram and view count but loses every
    average and its finishing place, so those come back as ``None``.
    """
    soup = soup if soup is not None else soupify(html)
    if _BREAKDOWN_START not in html:
        msg = "no voting-breakdown panel on the page; is the session logged in?"
        raise ImageStatsUnavailableError(msg)
    section = _breakdown_section(html)

    votes = tuple(
        int(clean_text(el)) for el in soup.find_all("div", {"class": "breakdown_vote_count"})
    )
    if votes and len(votes) != VOTE_BUCKETS:
        msg = f"expected {VOTE_BUCKETS} vote buckets, found {len(votes)}"
        raise ValueError(msg)

    disqualified = _DISQUALIFIED_MARKER not in section
    views = _int(section, "<b>Views since voting:</b> ")

    if disqualified:
        return ImageStats(votes=votes, disqualified=True, num_views=views)

    return ImageStats(
        votes=votes,
        disqualified=False,
        position=_int(section, "<b>Place:</b> "),
        average_all=_float(section, "<b>Avg (all users):</b> "),
        average_commenters=_float(section, "<b>Avg (commenters):</b> "),
        average_participants=_float(section, "<b>Avg (participants):</b> "),
        average_non_participants=_float(section, "<b>Avg (non-participants):</b> "),
        num_views=views,
        num_votes=_int(section, "<b>Votes:</b> "),
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


def _breakdown_section(html: str) -> str:
    _, marker, rest = html.partition(_BREAKDOWN_START)
    if not marker:
        return ""
    section, _, _ = rest.partition(_BREAKDOWN_END)
    return section


def _raw_number(section: str, label: str) -> str | None:
    if label not in section:
        return None
    match = re.search(_NUMBER, section.split(label, 1)[1])
    if match is None:
        return None
    return match.group(1).replace(",", "")


def _int(section: str, label: str) -> int | None:
    raw = _raw_number(section, label)
    # Some counts render as "7.0"; int() will not take that directly.
    return None if raw is None else int(float(raw))


def _float(section: str, label: str) -> float | None:
    raw = _raw_number(section, label)
    return None if raw is None else float(raw)
