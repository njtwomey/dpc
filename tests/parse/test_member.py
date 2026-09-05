from __future__ import annotations

from datetime import date

import pytest

from dpc.parse.member import MemberProfileUnavailableError, parse_member

# member/odriew.html is a real capture of USER_ID=75618.
ODRIEW_ID = 75618


class TestRealProfile:
    @pytest.fixture
    def member(self, html):
        return parse_member(html("member/odriew.html"), member_id=ODRIEW_ID)

    def test_takes_the_username_not_the_real_name(self, member):
        # The profile carries both: Name: "Jed" and Username: "odriew".
        assert member.name == "odriew"

    def test_join_date(self, member):
        # Rendered as "Mar. 16th 2007" -- ordinal suffix and a dotted month.
        assert member.join_date == date(2007, 3, 16)

    def test_identity_and_status(self, member):
        assert member.id == ODRIEW_ID
        assert member.cancelled is False


class TestFieldLookup:
    """Fields are found by their profile-heading label, not by position."""

    def test_reordering_rows_does_not_shift_values(self, html):
        page = html("member/odriew.html").replace(
            '<td class="profile-heading">Name:</td>', '<td class="profile-heading">Alias:</td>'
        )
        assert parse_member(page, ODRIEW_ID).name == "odriew"

    def test_a_value_spanning_lines_takes_the_first(self):
        page = (
            '<table><tr><td class="profile-heading">Username:</td>'
            "<td>someone<br>Photographer of the Year</td></tr>"
            '<tr><td class="profile-heading">Registered:</td><td>Jan. 1st 2004</td></tr></table>'
        )
        assert parse_member(page, 1).name == "someone"

    @pytest.mark.parametrize(
        ("rendered", "expected"),
        [
            ("Jan. 1st 2004", date(2004, 1, 1)),
            ("Feb. 2nd 2004", date(2004, 2, 2)),
            ("Mar. 3rd 2004", date(2004, 3, 3)),
            ("Apr. 4th 2004", date(2004, 4, 4)),
            ("Dec. 22nd 2024", date(2024, 12, 22)),
        ],
    )
    def test_every_ordinal_suffix_parses(self, rendered, expected):
        page = (
            '<table><tr><td class="profile-heading">Username:</td><td>x</td></tr>'
            f'<tr><td class="profile-heading">Registered:</td><td>{rendered}</td></tr></table>'
        )
        assert parse_member(page, 1).join_date == expected

    def test_a_profile_without_a_join_date_is_still_parsed(self):
        page = '<table><tr><td class="profile-heading">Username:</td><td>x</td></tr></table>'
        member = parse_member(page, 1)
        assert member.name == "x"
        assert member.join_date is None


class TestCancelledMembership:
    def test_has_no_fabricated_join_date(self, html):
        # The old parser stamped these with arrow.now().date(), writing a join
        # date that silently changed on every run.
        member = parse_member(html("member/cancelled.html"), member_id=999, fallback_name="ghost")

        assert member.cancelled is True
        assert member.join_date is None
        assert member.name == "ghost"


class TestUnparseablePages:
    def test_raises_and_reports_the_labels_it_did_find(self):
        page = '<table><tr><td class="profile-heading">Location:</td><td>Cork</td></tr></table>'
        with pytest.raises(MemberProfileUnavailableError, match="location"):
            parse_member(page, member_id=1)

    def test_an_empty_page_raises_rather_than_inventing_a_member(self):
        with pytest.raises(MemberProfileUnavailableError):
            parse_member("<html><body>nothing here</body></html>", member_id=1)


class TestRenamedMembers:
    """A member who has changed username gets two labels in one heading cell.

    Real markup from USER_ID=99687:
        <td class="profile-heading">Username:<br/>Formerly:<br/></td>
        <td>KristjanUnnar<br/>kiddiuk (Nov. 19th, 2025)</td>

    The label became "username:formerly" and matched nothing, so the member
    parsed with no name at all.
    """

    def test_takes_the_current_username(self, html):
        member = parse_member(html("member/renamed.html"), member_id=99687)
        assert member.name == "KristjanUnnar"

    def test_does_not_take_the_former_username(self, html):
        assert parse_member(html("member/renamed.html"), member_id=99687).name != "kiddiuk"

    def test_other_fields_still_resolve(self, html):
        member = parse_member(html("member/renamed.html"), member_id=99687)
        assert member.join_date == date(2005, 8, 3)
        assert member.cancelled is False

    def test_a_name_is_never_empty_for_a_readable_profile(self, html):
        for fixture in ("member/renamed.html", "member/odriew.html"):
            assert parse_member(html(fixture), member_id=1).name
