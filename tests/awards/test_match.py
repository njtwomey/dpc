from __future__ import annotations

from dpc.awards.catalog import AwardDefinition
from dpc.awards.match import awards_in, matches

BLUE = AwardDefinition(name="Posthumous Blue", markers=("blackyak.com/dpc/bluepost", "1077284"))
RED = AwardDefinition(name="Posthumous Red", markers=("blackyak.com/dpc/redpost", "1077285"))


def test_matches_on_an_embedded_image_url():
    comment = '<td>Lovely. <img src="http://blackyak.com/dpc/bluepost.gif"></td>'
    assert matches(comment, BLUE) is True
    assert matches(comment, RED) is False


def test_matches_on_a_bare_image_id():
    assert matches("<td>see 1077284</td>", BLUE) is True


def test_no_marker_no_match():
    assert matches("<td>Nice shot!</td>", BLUE) is False


def test_awards_in_returns_catalogue_order():
    comment = '<td><img src="redpost.gif"><img src="http://blackyak.com/dpc/bluepost.gif"></td>'
    comment += "1077285"
    assert [a.name for a in awards_in(comment, [BLUE, RED])] == [
        "Posthumous Blue",
        "Posthumous Red",
    ]


def test_matching_needs_the_html_not_the_text():
    # The marker lives in an img src, which text extraction throws away. This is
    # why comments keep their raw HTML.
    html = '<td><img src="http://blackyak.com/dpc/bluepost.gif"></td>'
    text = "Lovely."
    assert matches(html, BLUE) is True
    assert matches(text, BLUE) is False
