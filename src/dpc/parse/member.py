"""Parse a ``profile.php`` page into a :class:`MemberRecord`."""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from dpc.parse.text import clean_text, collapse_whitespace, parse_date, soupify, strip_ordinals
from dpc.parse.types import MemberRecord

_HEADING_CLASS = "profile-heading"
_USERNAME_LABEL = "username"
_REGISTERED_LABEL = "registered"

# "Mar. 16th 2007" is what the profile actually renders; the ordinal is stripped
# before parsing. The bare-month forms are accepted in case that ever changes.
_JOIN_DATE_FORMATS = ("%b. %d %Y", "%b %d %Y", "%B %d %Y", "%B. %d %Y")


class MemberProfileUnavailableError(Exception):
    """The page carried no profile table and no cancellation notice."""


def parse_member(html: str, member_id: int, *, fallback_name: str = "") -> MemberRecord:
    """Parse a member profile.

    Fields are looked up by their ``td.profile-heading`` label rather than by
    position, so an added or reordered row cannot shift the values into the
    wrong columns.

    A cancelled membership renders a red-font notice instead of the profile
    table. The old parser handled that by stamping the member with
    ``arrow.now().date()``, fabricating a join date that changed on every run;
    a cancelled member now has ``join_date=None`` and ``cancelled=True``.
    """
    soup = soupify(html)
    fields = _profile_fields(soup)

    if _USERNAME_LABEL not in fields:
        if soup.find("font", {"color": "red"}) is not None:
            return MemberRecord(id=member_id, name=fallback_name, join_date=None, cancelled=True)
        msg = (
            f"member {member_id}: no '{_USERNAME_LABEL}' row and no cancellation "
            f"notice; labels present: {sorted(fields)}"
        )
        raise MemberProfileUnavailableError(msg)

    name = fields[_USERNAME_LABEL] or fallback_name

    join_date = None
    registered = fields.get(_REGISTERED_LABEL)
    if registered:
        join_date = parse_date(strip_ordinals(registered), *_JOIN_DATE_FORMATS)

    return MemberRecord(id=member_id, name=name, join_date=join_date, cancelled=False)


def _profile_fields(soup: BeautifulSoup) -> dict[str, str]:
    """``{lowercased label without colon: value}`` from the profile table."""
    fields: dict[str, str] = {}
    for cell in soup.find_all("td", {"class": _HEADING_CLASS}):
        value_cell = cell.find_next_sibling("td")
        if value_cell is None:
            continue
        # A member who has renamed gets two labels in one cell:
        # "Username:<br/>Formerly:<br/>", against a value cell holding both.
        # Take the text before the first colon, which is the label that governs
        # the first value -- and _cell_value already stops at the first <br>.
        label = clean_text(cell).split(":")[0].strip().lower()
        if label and label not in fields:
            fields[label] = _cell_value(value_cell)
    return fields


def _cell_value(cell: Tag) -> str:
    """The cell's text up to its first ``<br>``.

    Profile cells put the value first and anything else -- a rank, a second
    camera -- after a line break. Splitting on the tag rather than on newlines
    matters because ``odriew<br>Rank`` carries no whitespace to split on.
    """
    parts: list[str] = []
    for child in cell.children:
        if getattr(child, "name", None) == "br":
            break
        parts.append(child.get_text() if isinstance(child, Tag) else str(child))
    return collapse_whitespace("".join(parts))
