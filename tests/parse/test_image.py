from __future__ import annotations

from datetime import datetime

import pytest

from dpc.parse.image import parse_comments, parse_image, parse_image_stats
from dpc.parse.types import VOTE_BUCKETS


class TestParseImage:
    def test_parses_identity_and_photographer(self, html):
        image = parse_image(html("image/scored.html"), image_id=921974, challenge_id=1303)

        assert image.id == 921974
        assert image.challenge_id == 1303
        assert image.photographer_id == 75618
        assert image.name == "Disconnect"

    def test_missing_photographer_link_raises(self):
        with pytest.raises(ValueError, match="photographer link"):
            parse_image("<html><body></body></html>", image_id=1, challenge_id=1)


class TestParseImageStats:
    def test_scored_image_has_every_average(self, html):
        stats = parse_image_stats(html("image/scored.html"))

        assert stats.disqualified is False
        assert stats.position == 7
        assert stats.average_all == pytest.approx(5.9432)
        assert stats.average_commenters == pytest.approx(6.1)
        assert stats.average_participants == pytest.approx(5.8)
        assert stats.average_non_participants == pytest.approx(6.05)
        assert stats.num_votes == 234

    def test_view_count_survives_a_thousands_separator(self, html):
        # The old regex was ([\d\.]+), which stopped dead at the comma, so
        # "Views since voting: 1,234" was recorded as 1.
        stats = parse_image_stats(html("image/scored.html"))
        assert stats.num_views == 1234

    def test_disqualified_image_keeps_votes_and_views_but_loses_averages(self, html):
        stats = parse_image_stats(html("image/disqualified.html"))

        assert stats.disqualified is True
        assert stats.num_views == 87
        assert len(stats.votes) == VOTE_BUCKETS
        assert stats.position is None
        assert stats.average_all is None
        assert stats.average_commenters is None
        assert stats.average_participants is None
        assert stats.average_non_participants is None
        assert stats.num_votes is None

    def test_vote_histogram_always_has_ten_buckets(self, html):
        stats = parse_image_stats(html("image/scored.html"))
        assert stats.votes == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

    def test_wrong_bucket_count_is_rejected(self):
        page = (
            '<td>Voting Breakdown <span style="font-weight: normal;">'
            '<div class="breakdown_vote_count">1</div>'
            "<b>Avg (all users):</b> 5.0"
            '<td valign="top" width="450" class="textsm">'
        )
        with pytest.raises(ValueError, match="vote buckets"):
            parse_image_stats(page)


class TestParseComments:
    def test_returns_nothing_when_there_is_no_comment_table(self, html):
        assert parse_comments(html("image/no_comments.html"), image_id=1) == []

    def test_parses_both_comments(self, html):
        comments = parse_comments(html("image/scored.html"), image_id=921974)
        assert [c.id for c in comments] == [900001, 900002]

    def test_captures_commenter_identity(self, html):
        first, _ = parse_comments(html("image/scored.html"), image_id=921974)
        assert first.commenter_id == 50695
        assert first.commenter_name == "posthumous"
        assert first.image_id == 921974

    def test_timestamp_is_parsed_from_the_12_hour_format(self, html):
        first, second = parse_comments(html("image/scored.html"), image_id=921974)
        assert first.date == datetime(2004, 1, 9, 22, 30, 0)
        assert second.date == datetime(2004, 1, 20, 9, 15, 0)

    def test_edit_marker_is_split_off_the_body(self, html):
        _, second = parse_comments(html("image/scored.html"), image_id=921974)
        assert second.comment == "Congratulations!"
        assert second.edited == datetime(2004, 1, 21, 11, 0, 0)

    def test_unedited_comment_has_no_edit_timestamp(self, html):
        first, _ = parse_comments(html("image/scored.html"), image_id=921974)
        assert first.edited is None

    def test_during_challenge_flag_follows_the_divider_row(self, html):
        comments = parse_comments(html("image/scored.html"), image_id=921974)
        assert all(c.made_during_challenge for c in comments)

    def test_raw_comment_keeps_the_html_award_markers_live_in(self, html):
        # Award matching runs against raw_comment, because the markers are image
        # URLs that vanish under text extraction.
        first, _ = parse_comments(html("image/scored.html"), image_id=921974)
        assert "blackyak.com/dpc/bluepost" in first.raw_comment
        assert "blackyak.com/dpc/bluepost" not in first.comment
