"""Parse an ``image.php`` page: the vote breakdown, the stats, and the comments."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

from dpc.parse.text import clean_text, parse_datetime, soupify
from dpc.parse.types import VOTE_BUCKETS, CommentRecord, ImageRecord, ImageStats

_BREAKDOWN_START = '<td>Voting Breakdown <span style="font-weight: normal;">'
_BREAKDOWN_END = '<td valign="top" width="450" class="textsm">'

_DISQUALIFIED_MARKER = "Avg (all users)"
_DURING_CHALLENGE_MARKER = "Comments Made During the Challenge"
_EDITED_MARKER = "Message edited by author "

_USER_ID = re.compile(r"USER_ID=(\d+)")
_COMMENT_TABLE = {
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


def parse_image(html: str, image_id: int, challenge_id: int) -> ImageRecord:
    soup = soupify(html)

    title = clean_text(soup.find("div", {"class": "imagetitle"}))

    user_links = soup.find_all("a", {"class": "u"})
    if len(user_links) < 2:
        msg = f"image {image_id}: could not find the photographer link"
        raise ValueError(msg)
    match = _USER_ID.search(str(user_links[1].get("href", "")))
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
    section = _breakdown_section(html)

    votes = tuple(int(clean_text(el)) for el in soup.find_all("div", {"class": "breakdown_vote_count"}))
    if votes and len(votes) != VOTE_BUCKETS:
        msg = f"expected {VOTE_BUCKETS} vote buckets, found {len(votes)}"
        raise ValueError(msg)

    disqualified = _DISQUALIFIED_MARKER not in section
    views = _number(section, "<b>Views since voting:</b> ", int)

    if disqualified:
        return ImageStats(votes=votes, disqualified=True, num_views=views)

    return ImageStats(
        votes=votes,
        disqualified=False,
        position=_number(section, "<b>Place:</b> ", int),
        average_all=_number(section, "<b>Avg (all users):</b> ", float),
        average_commenters=_number(section, "<b>Avg (commenters):</b> ", float),
        average_participants=_number(section, "<b>Avg (participants):</b> ", float),
        average_non_participants=_number(section, "<b>Avg (non-participants):</b> ", float),
        num_views=views,
        num_votes=_number(section, "<b>Votes:</b> ", int),
    )


def parse_comments(html: str, image_id: int, soup: BeautifulSoup | None = None) -> list[CommentRecord]:
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
        if len(links) < 3:
            continue
        commenter_link = links[2]
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
                id=int(anchor.attrs["name"]),
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


def _split_edited(text: str) -> tuple[str, object]:
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


def _number(section: str, label: str, cast: type):  # type: ignore[no-untyped-def]
    if label not in section:
        return None
    match = re.search(_NUMBER, section.split(label, 1)[1])
    if match is None:
        return None
    raw = match.group(1).replace(",", "")
    return cast(float(raw)) if cast is int else cast(raw)
