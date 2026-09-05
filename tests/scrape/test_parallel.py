from __future__ import annotations

from pathlib import Path

import pytest

from dpc.scrape.parallel import FailedImage, ParsedImage, parse_images, parse_one

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "html"
SCORED = (FIXTURES / "image" / "scored.html").read_text(encoding="utf-8")
ANONYMOUS = (FIXTURES / "image" / "anonymous.html").read_text(encoding="utf-8")


class TestParseOne:
    def test_parses_a_good_page(self):
        result = parse_one(SCORED, 1287065, 3729)
        assert isinstance(result, ParsedImage)
        assert result.image.id == 1287065
        assert result.image.name == "So Many Geese!"

    def test_returns_a_failure_rather_than_raising(self):
        # A pool that dies mid-map loses the whole batch.
        result = parse_one("<html>nothing at all</html>", 1, 1)
        assert isinstance(result, FailedImage)
        assert result.image_id == 1

    def test_flags_a_missing_stats_panel_distinctly(self):
        # A complete page apart from the panel: means the page shape changed,
        # not that this one image is odd, so the caller stops rather than
        # logging and carrying on.
        page = (
            '<div class="imagetitle">T</div><a class="u" href="profile.php?USER_ID=42">someone</a>'
        )
        result = parse_one(page, 1, 1)
        assert isinstance(result, FailedImage)
        assert result.unavailable_stats is True

    def test_an_ordinary_failure_is_not_flagged_that_way(self):
        # Has a stats panel, but no link carrying a USER_ID.
        page = (
            '<div class="imagetitle">T</div>'
            '<table><tr class="forum-heading"><td>Statistics</td></tr>'
            "<tr><td><b>Avg (all users):</b> 5.0</td></tr></table>"
        )
        result = parse_one(page, 1, 1)
        assert isinstance(result, FailedImage)
        assert result.unavailable_stats is False


class TestParseImages:
    def test_empty_input(self):
        assert parse_images([]) == []

    def test_serial_preserves_order(self):
        pages = [(SCORED, 1, 3729), (ANONYMOUS, 2, 1303), (SCORED, 3, 3729)]
        results = parse_images(pages, workers=0)

        assert all(isinstance(r, ParsedImage) for r in results)
        assert [r.image.id for r in results if isinstance(r, ParsedImage)] == [1, 2, 3]

    @pytest.mark.slow
    def test_processes_give_the_same_answer_as_serial(self):
        pages = [(SCORED, i, 3729) for i in range(1, 9)]
        serial = [r for r in parse_images(pages, workers=0) if isinstance(r, ParsedImage)]
        parallel = [r for r in parse_images(pages, workers=2) if isinstance(r, ParsedImage)]

        assert len(serial) == len(pages)
        assert [r.image.id for r in serial] == [r.image.id for r in parallel]
        assert [r.image.stats for r in serial] == [r.image.stats for r in parallel]

    def test_a_bad_page_does_not_sink_the_batch(self):
        pages = [(SCORED, 1, 3729), ("<html>bad</html>", 2, 3729), (SCORED, 3, 3729)]
        results = parse_images(pages, workers=0)

        assert isinstance(results[1], FailedImage)
        assert isinstance(results[0], ParsedImage)
        assert isinstance(results[2], ParsedImage)
