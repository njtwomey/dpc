from __future__ import annotations

from datetime import date

import pytest

from dpc.parse.member import parse_member


def test_parses_name_and_join_date(html):
    member = parse_member(html("member/normal.html"), member_id=117474)

    assert member.id == 117474
    assert member.name == "NiallOTuama"
    assert member.join_date == date(2004, 1, 1)
    assert member.cancelled is False


def test_name_excludes_the_rank_that_follows_it(html):
    member = parse_member(html("member/normal.html"), member_id=117474)
    assert "Enthusiast" not in member.name


def test_cancelled_membership_has_no_fabricated_join_date(html):
    # The old parser stamped these with arrow.now().date(), writing a join date
    # that silently changed on every single run.
    member = parse_member(html("member/cancelled.html"), member_id=999, fallback_name="ghost")

    assert member.cancelled is True
    assert member.join_date is None
    assert member.name == "ghost"


def test_unrecognised_profile_raises(html):
    with pytest.raises(ValueError, match="profile detail table"):
        parse_member("<html><body>nothing here</body></html>", member_id=1)
