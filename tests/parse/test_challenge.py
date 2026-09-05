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


class TestClassify:
    def test_invalid_id_page(self, html):
        assert classify(html("challenge/invalid.html")) is ChallengePage.INVALID

    def test_unfinished_challenge_page(self, html):
        # A real capture of CHALLENGE_ID=3882 while the challenge was still open.
        assert classify(html("challenge/unfinished.html")) is ChallengePage.UNFINISHED

    def test_results_page(self, html):
        assert classify(html("challenge/results.html")) is ChallengePage.RESULTS


class TestParseChallenge:
    def test_parses_every_field(self, html):
        challenge = parse_challenge(html("challenge/results.html"), challenge_id=2512)

        assert challenge.id == 2512
        assert challenge.name == "Hidden Gem VI — Mid-Term Quiz"
        assert challenge.description == "Photograph something that is hidden in plain sight."
        assert challenge.submission_start == date(2004, 1, 1)
        assert challenge.submission_end == date(2004, 1, 7)
        assert challenge.voting_start == date(2004, 1, 8)
        assert challenge.voting_end == date(2004, 1, 14)
        assert challenge.num_submissions == 123
        assert challenge.num_disqualifications == 4
        assert challenge.num_votes == 12345
        assert challenge.num_comments == 678
        assert challenge.average_score == pytest.approx(5.1234)
        assert challenge.highest_score == pytest.approx(8.5)
        assert challenge.median_score == pytest.approx(5.0)
        assert challenge.lowest_score == pytest.approx(1.2)

    def test_name_keeps_its_em_dash(self, html):
        # The shipped site had "Hidden Gem VI \x97 Mid-Term Quiz" because the
        # bytes were decoded with the wrong codec upstream of the parser.
        challenge = parse_challenge(html("challenge/results.html"), challenge_id=2512)
        assert "—" in challenge.name
        assert "\x97" not in challenge.name

    def test_description_whitespace_is_collapsed(self, html):
        challenge = parse_challenge(html("challenge/results.html"), challenge_id=2512)
        assert "\n" not in challenge.description
        assert "  " not in challenge.description

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


class TestParseImageIds:
    def test_deduplicates_preserving_order(self, html):
        # The old builder emitted duplicates and let a Hugo `uniq` hide them.
        assert parse_image_ids(html("challenge/results.html")) == (1202898, 1203340)

    def test_ignores_non_image_links(self, html):
        assert 9 not in parse_image_ids(html("challenge/results.html"))

    def test_empty_when_there_are_none(self, html):
        assert parse_image_ids(html("challenge/invalid.html")) == ()
