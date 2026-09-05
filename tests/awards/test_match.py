from __future__ import annotations

from pathlib import Path

import pytest

from dpc.awards.catalog import AwardDefinition
from dpc.awards.match import awards_in, matches, strip_quotes

COMMENTS = Path(__file__).resolve().parents[1] / "fixtures" / "html" / "comment"

ASIGMATIC = AwardDefinition(
    name="Asigmatic",
    markers=("Copyrighted_Image_Reuse_Prohibited_1000203", "1000203"),
)
BLUE = AwardDefinition(name="Posthumous Blue", markers=("blackyak.com/dpc/bluepost", "1077284"))
RED = AwardDefinition(name="Posthumous Red", markers=("blackyak.com/dpc/redpost", "1077285"))


@pytest.fixture(scope="module")
def comment():
    def _read(name: str) -> str:
        return (COMMENTS / name).read_text(encoding="utf-8")

    return _read


class TestBasicMatching:
    def test_matches_on_an_embedded_image_url(self):
        assert matches('<td><img src="http://blackyak.com/dpc/bluepost.gif"></td>', BLUE) is True

    def test_does_not_match_a_different_award(self):
        assert matches('<td><img src="http://blackyak.com/dpc/bluepost.gif"></td>', RED) is False

    def test_matches_on_a_bare_image_id(self):
        assert matches("<td>see 1077284</td>", BLUE) is True

    def test_no_marker_no_match(self):
        assert matches("<td>Nice shot!</td>", BLUE) is False

    def test_needs_the_html_not_the_text(self):
        # The marker lives in an img src, which text extraction throws away.
        assert matches('<td><img src="http://blackyak.com/dpc/bluepost.gif"></td>', BLUE) is True
        assert matches("Lovely.", BLUE) is False

    def test_awards_in_returns_catalogue_order(self):
        html = '<td><img src="redpost.gif">1077285<img src="blackyak.com/dpc/bluepost.gif"></td>'
        assert [a.name for a in awards_in(html, [BLUE, RED])] == [
            "Posthumous Blue",
            "Posthumous Red",
        ]


class TestRealAwardComments:
    """Real comments from the archive."""

    def test_an_award_comment_matches(self, comment):
        assert matches(comment("award_original.html"), ASIGMATIC) is True

    def test_a_double_submit_is_identical_to_the_original(self, comment):
        # Comment 7034993 was posted four seconds after 7034991, byte for byte
        # the same. Both match; collapsing them is the storage layer's job, not
        # the matcher's.
        assert comment("award_duplicate.html") == comment("award_original.html")
        assert matches(comment("award_duplicate.html"), ASIGMATIC) is True


class TestQuotedAwardsDoNotCount:
    """Quoting an award copies its image, which would award it twice.

    Live example: https://www.dpchallenge.com/image.php?IMAGE_ID=1160121
    """

    def test_a_reply_that_only_quotes_an_award_does_not_match(self, comment):
        raw = comment("quote_only.html")
        assert "1000203" in raw, "the marker really is present in the raw html"
        assert matches(raw, ASIGMATIC) is False

    def test_the_quoted_block_is_removed(self, comment):
        assert "Originally posted by" not in strip_quotes(comment("quote_only.html"))

    def test_text_outside_the_quote_survives(self, comment):
        assert "Congratulations" in strip_quotes(comment("quote_only.html"))

    def test_a_reply_that_also_awards_again_still_matches(self, comment):
        # Comment 7035001 quotes the earlier award and then says "Heck, I may as
        # well give it to you a third time", with the image outside the quote.
        assert matches(comment("quote_reply.html"), ASIGMATIC) is True

    def test_comments_without_quotes_are_returned_untouched(self):
        raw = '<td valign="top">Nice one.</td>'
        assert strip_quotes(raw) is raw

    def test_a_table_that_is_not_a_quote_is_left_alone(self):
        raw = '<td><table align="left" width="50%"><tr><td>1077284</td></tr></table></td>'
        assert matches(raw, BLUE) is True
