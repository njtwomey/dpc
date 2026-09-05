"""Parse ``challenge_history.php`` -- the index of every challenge."""

from __future__ import annotations

import re

from dpc.parse.text import soupify

_RESULTS_HREF = re.compile(r"/challenge_results\.php\?CHALLENGE_ID=(\d+)")


def parse_challenge_ids(html: str) -> tuple[int, ...]:
    """Challenge ids listed on a history page, de-duplicated, order preserved."""
    soup = soupify(html)
    seen: dict[int, None] = {}
    for link in soup.find_all("a", href=_RESULTS_HREF):
        match = _RESULTS_HREF.search(str(link.get("href", "")))
        if match:
            seen.setdefault(int(match.group(1)), None)
    return tuple(seen)
