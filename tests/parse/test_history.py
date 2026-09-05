from __future__ import annotations

from dpc.parse.history import parse_challenge_ids


def test_extracts_ids_deduplicated_in_order(html):
    assert parse_challenge_ids(html("history/page.html")) == (3880, 3881)


def test_ignores_unrelated_links(html):
    assert parse_challenge_ids('<a href="/forum.php">x</a>') == ()
