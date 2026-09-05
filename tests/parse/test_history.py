from __future__ import annotations

from dpc.parse.history import parse_challenge_ids

# history/page.html is a real capture of challenge_history.php, trimmed to the
# first 60 rows (the full page is 2.7 MB of anchors).


class TestRealHistory:
    def test_reads_every_row(self, html):
        assert len(parse_challenge_ids(html("history/page.html"))) == 60

    def test_is_not_assumed_to_be_sorted(self, html):
        # The real page interleaves still-open challenges (4193-4197) among the
        # finished ones, so nothing downstream may rely on the order.
        ids = parse_challenge_ids(html("history/page.html"))
        assert ids != tuple(sorted(ids, reverse=True))

    def test_ids_are_positive_challenge_numbers(self, html):
        ids = parse_challenge_ids(html("history/page.html"))
        assert all(i > 0 for i in ids)

    def test_ids_are_unique(self, html):
        ids = parse_challenge_ids(html("history/page.html"))
        assert len(ids) == len(set(ids))


class TestExtraction:
    def test_deduplicates_preserving_order(self):
        page = (
            '<a href="/challenge_results.php?CHALLENGE_ID=3880">a</a>'
            '<a href="/challenge_results.php?CHALLENGE_ID=3881">b</a>'
            '<a href="/challenge_results.php?CHALLENGE_ID=3880">a again</a>'
        )
        assert parse_challenge_ids(page) == (3880, 3881)

    def test_ignores_unrelated_links(self):
        assert parse_challenge_ids('<a href="/forum.php">x</a>') == ()
