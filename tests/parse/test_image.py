from __future__ import annotations

from datetime import datetime

import pytest

from dpc.parse.image import (
    ImageStatsUnavailableError,
    parse_comments,
    parse_image,
    parse_image_stats,
)
from dpc.parse.types import VOTE_BUCKETS

# image/anonymous.html is a real capture of IMAGE_ID=921974 ("Disconnect" by
# odriew, challenge 1303), fetched without a session. The voting-breakdown panel
# is served only to logged-in users, so that page has comments but no scores.
IMAGE_ID = 921974
CHALLENGE_ID = 1303
PHOTOGRAPHER_ID = 75618


class TestRealPage:
    def test_identity_and_photographer(self, html):
        # parse_image needs the stats panel, so read the pieces it can reach.
        page = html("image/anonymous.html")
        comments = parse_comments(page, IMAGE_ID)
        assert comments, "the real page should carry comments"
        assert all(c.image_id == IMAGE_ID for c in comments)

    def test_stats_panel_absence_is_not_a_disqualification(self, html):
        # The crucial distinction. An anonymous page has no panel at all; a
        # disqualified image HAS the panel but no averages. Reading one as the
        # other would mark the entire archive disqualified.
        with pytest.raises(ImageStatsUnavailableError):
            parse_image_stats(html("image/anonymous.html"))

    def test_parse_image_propagates_that_rather_than_guessing(self, html):
        # The old parser split on the panel marker and indexed [1], so this
        # raised a bare IndexError that the caller swallowed with a print.
        with pytest.raises(ImageStatsUnavailableError):
            parse_image(html("image/anonymous.html"), IMAGE_ID, CHALLENGE_ID)


class TestRealComments:
    @pytest.fixture
    def comments(self, html):
        return parse_comments(html("image/anonymous.html"), IMAGE_ID)

    def test_reads_the_whole_thread(self, comments):
        assert len(comments) == 29

    def test_ids_are_unique(self, comments):
        assert len({c.id for c in comments}) == len(comments)

    def test_captures_commenter_identity(self, comments):
        first = comments[0]
        assert first.commenter_name == "Neat"
        assert first.commenter_id == 114285

    def test_parses_the_12_hour_timestamp(self, comments):
        assert comments[0].date == datetime(2013, 2, 3, 20, 14, 44)

    def test_extracts_the_comment_text(self, comments):
        assert comments[0].comment == "Sensational!"

    def test_keeps_the_raw_html_for_award_matching(self, comments):
        # Award markers are image and anchor URLs that text extraction discards.
        assert comments[0].raw_comment.startswith("<td")

    def test_every_comment_has_a_commenter_and_a_date(self, comments):
        assert all(c.commenter_id > 0 for c in comments)
        assert all(c.date is not None for c in comments)


class TestStatsFromASyntheticPanel:
    """The panel is login-only, so these use fixtures built to its markup."""

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
        assert parse_image_stats(html("image/scored.html")).num_views == 1234

    def test_disqualified_image_keeps_votes_and_views_but_loses_averages(self, html):
        stats = parse_image_stats(html("image/disqualified.html"))

        assert stats.disqualified is True
        assert stats.num_views == 87
        assert len(stats.votes) == VOTE_BUCKETS
        assert stats.position is None
        assert stats.average_all is None
        assert stats.num_votes is None

    def test_vote_histogram_has_ten_buckets(self, html):
        assert parse_image_stats(html("image/scored.html")).votes == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

    def test_wrong_bucket_count_is_rejected(self):
        page = (
            '<td>Voting Breakdown <span style="font-weight: normal;">'
            '<div class="breakdown_vote_count">1</div>'
            "<b>Avg (all users):</b> 5.0"
            '<td valign="top" width="450" class="textsm">'
        )
        with pytest.raises(ValueError, match="vote buckets"):
            parse_image_stats(page)

    def test_identity_and_photographer(self, html):
        image = parse_image(html("image/scored.html"), image_id=IMAGE_ID, challenge_id=CHALLENGE_ID)
        assert image.id == IMAGE_ID
        assert image.challenge_id == CHALLENGE_ID
        assert image.photographer_id == PHOTOGRAPHER_ID
        assert image.name == "Disconnect"


class TestSyntheticComments:
    """Cases the real capture does not happen to contain."""

    def test_no_comment_table_yields_nothing(self, html):
        assert parse_comments(html("image/no_comments.html"), image_id=1) == []

    def test_edit_marker_is_split_off_the_body(self, html):
        _, second = parse_comments(html("image/scored.html"), image_id=IMAGE_ID)
        assert second.comment == "Congratulations!"
        assert second.edited == datetime(2004, 1, 21, 11, 0, 0)

    def test_unedited_comment_has_no_edit_timestamp(self, html):
        first, _ = parse_comments(html("image/scored.html"), image_id=IMAGE_ID)
        assert first.edited is None

    def test_during_challenge_flag_follows_the_divider_row(self, html):
        comments = parse_comments(html("image/scored.html"), image_id=IMAGE_ID)
        assert all(c.made_during_challenge for c in comments)

    def test_award_markers_survive_only_in_the_raw_html(self, html):
        first, _ = parse_comments(html("image/scored.html"), image_id=IMAGE_ID)
        assert "blackyak.com/dpc/bluepost" in first.raw_comment
        assert "blackyak.com/dpc/bluepost" not in first.comment
