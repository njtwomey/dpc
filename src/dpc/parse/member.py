"""Parse a ``profile.php`` page into a :class:`MemberRecord`."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from bs4 import Tag

from dpc.parse.text import clean_text, parse_date, soupify, strip_ordinals
from dpc.parse.types import MemberRecord

_REGISTERED_LABEL = "Registered:"
_USERNAME_LABEL = "Username:"
_PROFILE_TABLE: dict[str, Any] = {"cellspacing": "5", "cellpadding": "0", "width": "100%"}

_JOIN_DATE_FORMATS = ("%b. %d %Y", "%b %d %Y", "%B %d %Y")


def parse_member(html: str, member_id: int, *, fallback_name: str = "") -> MemberRecord:
    """Parse a member profile.

    A cancelled membership renders a red-font notice instead of the profile
    table. The old parser handled that by stamping the member with
    ``arrow.now().date()``, fabricating a join date that changed on every run.
    Here a cancelled member gets ``join_date=None`` and ``cancelled=True``.
    """
    soup = soupify(html)

    if soup.find("font", {"color": "red"}) is not None:
        return MemberRecord(
            id=member_id,
            name=fallback_name,
            join_date=None,
            cancelled=True,
        )

    outer = soup.find("table", _PROFILE_TABLE)
    inner = outer.find("table") if outer is not None else None
    cells = inner.find_all("td") if inner is not None else []
    if not cells:
        msg = f"member {member_id}: could not locate the profile detail table"
        raise ValueError(msg)

    name = _value_after(cells, _USERNAME_LABEL, member_id)
    registered = _value_after(cells, _REGISTERED_LABEL, member_id)

    return MemberRecord(
        id=member_id,
        # The username cell also carries the member's title/rank after the name.
        name=name.split()[0] if name.split() else fallback_name,
        join_date=parse_date(strip_ordinals(registered), *_JOIN_DATE_FORMATS),
        cancelled=False,
    )


def _value_after(cells: Sequence[Tag], label: str, member_id: int) -> str:
    """Return the text of the cell following the one containing ``label``."""
    for index, cell in enumerate(cells[:-1]):
        if label in clean_text(cell):
            return clean_text(cells[index + 1])
    msg = f"member {member_id}: no cell labelled {label!r}"
    raise ValueError(msg)
