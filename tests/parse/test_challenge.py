from __future__ import annotations

from datetime import date

import pytest

from dpc.parse.challenge import (
    ChallengeNotAvailableError,
    ChallengePage,
    classify,
    parse_challenge,
    parse_image_ids,
)

# challenge/results.html is a real capture of CHALLENGE_ID=1303, "Posthumous
# Ribbon" (Nov 2010). Every expected value below was read off that page.
RESULTS_ID = 1303


class TestClassify:
    def test_invalid_id_page(self, html):
        # A real "Invalid CHALLENGE_ID" response (CHALLENGE_ID=75).
        assert classify(html("challenge/invalid.html")) is ChallengePage.INVALID

    def test_unfinished_challenge_page(self, html):
        # A real capture of CHALLENGE_ID=3882 while the challenge was still open.
        assert classify(html("challenge/unfinished.html")) is ChallengePage.UNFINISHED

    def test_results_page(self, html):
        assert classify(html("challenge/results.html")) is ChallengePage.RESULTS


class TestParseChallenge:
    @pytest.fixture
    def challenge(self, html):
        return parse_challenge(html("challenge/results.html"), challenge_id=RESULTS_ID)

    def test_identity(self, challenge):
        assert challenge.id == RESULTS_ID
        assert challenge.name == "Posthumous Ribbon"

    def test_description_drops_the_bold_heading_above_it(self, challenge):
        # The div opens with <b>Description</b><br/>, which is a label, not text.
        assert challenge.description == (
            "Submit a photo that you think could win a Posthumous Ribbon."
        )
        assert not challenge.description.startswith("Description")

    def test_dates(self, challenge):
        assert challenge.submission_start == date(2010, 11, 19)
        assert challenge.submission_end == date(2010, 11, 25)
        assert challenge.voting_start == date(2010, 11, 26)
        assert challenge.voting_end == date(2010, 12, 2)

    def test_counts(self, challenge):
        assert challenge.num_submissions == 133
        assert challenge.num_disqualifications == 0
        assert challenge.num_votes == 23001  # rendered as "23,001"
        assert challenge.num_comments == 1867  # rendered as "1,867"

    def test_scores(self, challenge):
        assert challenge.average_score == pytest.approx(5.50554)
        assert challenge.highest_score == pytest.approx(6.7797)
        assert challenge.median_score == pytest.approx(5.4673)
        assert challenge.lowest_score == pytest.approx(3.9167)

    def test_thousands_separators_do_not_truncate_counts(self, challenge):
        # "23,001" must not become 23.
        assert challenge.num_votes > 1000

    @pytest.mark.parametrize(
        ("fixture", "kind"),
        [
            ("challenge/invalid.html", ChallengePage.INVALID),
            ("challenge/unfinished.html", ChallengePage.UNFINISHED),
        ],
    )
    def test_refuses_pages_without_results(self, html, fixture, kind):
        with pytest.raises(ChallengeNotAvailableError) as excinfo:
            parse_challenge(html(fixture), challenge_id=1)
        assert excinfo.value.kind is kind

    def test_missing_stats_label_names_the_labels_it_found(self):
        page = (
            '<tr class="forum-heading"><td>Challenge Results for X</td></tr>'
            '<div style="margin: 2px;">Submission Dates: Jan 1 2004 - Jan 7 2004</div>'
        )
        with pytest.raises(ValueError, match="labels present"):
            parse_challenge(page, challenge_id=7)

    def test_labels_are_matched_by_keyword_not_position(self, html):
        # The old parser indexed a ten-element list by position, so one inserted
        # row silently shifted every value into the wrong field.
        page = html("challenge/results.html").replace("Submissions:", "Total Submissions:")
        assert parse_challenge(page, RESULTS_ID).num_submissions == 133


class TestParseImageIds:
    def test_finds_every_entry(self, html):
        ids = parse_image_ids(html("challenge/results.html"))
        assert len(ids) == 133  # matches the challenge's own submission count

    def test_ids_are_unique(self, html):
        # The old builder emitted duplicates and let a Hugo `uniq` hide them.
        ids = parse_image_ids(html("challenge/results.html"))
        assert len(ids) == len(set(ids))

    def test_ignores_non_image_links(self, html):
        page = (
            '<a class="i" href="/image.php?IMAGE_ID=5">yes</a>'
            '<a class="i" href="/challenge_submit_preview.php?CHALLENGE_ID=9">no</a>'
        )
        assert parse_image_ids(page) == (5,)

    def test_deduplicates_preserving_order(self):
        page = (
            '<a class="i" href="/image.php?IMAGE_ID=2">a</a>'
            '<a class="i" href="/image.php?IMAGE_ID=1">b</a>'
            '<a class="i" href="/image.php?IMAGE_ID=2">a again</a>'
        )
        assert parse_image_ids(page) == (2, 1)

    def test_empty_when_there_are_none(self, html):
        assert parse_image_ids(html("challenge/invalid.html")) == ()
