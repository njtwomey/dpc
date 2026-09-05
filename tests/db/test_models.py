from __future__ import annotations

from datetime import date, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dpc.db import Award, AwardGrant, Challenge, Comment, Image, Member


def test_schema_creates_cleanly(session):
    assert session.scalars(select(Member)).all() == []


def test_vote_histogram_round_trips_as_json(session, image):
    stored = session.get(Image, image.id)
    assert stored is not None
    assert stored.votes == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert all(isinstance(v, int) for v in stored.votes)


def test_cancelled_member_keeps_a_null_join_date(session):
    session.add(Member(id=999, name="ghost", join_date=None, cancelled=True))
    session.commit()

    ghost = session.get(Member, 999)
    assert ghost is not None
    assert ghost.join_date is None
    assert ghost.cancelled is True


def test_relationships_navigate(session, image):
    stored = session.get(Image, image.id)
    assert stored is not None
    assert stored.challenge.name == "Test Challenge"
    assert stored.photographer.name == "photographer"


def test_an_award_cannot_be_granted_twice_on_one_comment(session, image):
    award = Award(awarder_id=1, name="Blue", slug="blue", markers=["bluepost"])
    session.add(award)
    comment = Comment(
        id=5001,
        image_id=image.id,
        commenter_id=1,
        raw_comment="<td>x</td>",
        comment="x",
        date=datetime(2004, 1, 9, 22, 30),
    )
    session.add(comment)
    session.commit()

    def grant() -> AwardGrant:
        return AwardGrant(
            award_id=award.id,
            recipient_id=image.photographer_id,
            comment_id=comment.id,
            image_id=image.id,
            challenge_id=image.challenge_id,
        )

    session.add(grant())
    session.commit()

    session.add(grant())
    with pytest.raises(IntegrityError):
        session.commit()


def test_award_slug_is_unique(session):
    session.add(Member(id=1, name="awarder", join_date=date(2004, 1, 1)))
    session.add(Award(awarder_id=1, name="Blue", slug="blue"))
    session.commit()

    session.add(Award(awarder_id=1, name="Blue Two", slug="blue"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_challenge_round_trips_dates(session):
    session.add(
        Challenge(
            id=42,
            name="Dates",
            description="",
            submission_start=date(2004, 1, 1),
            submission_end=date(2004, 1, 7),
            voting_start=date(2004, 1, 8),
            voting_end=date(2004, 1, 14),
            num_submissions=1,
            num_disqualifications=0,
            num_votes=2,
            num_comments=3,
            average_score=5.0,
            highest_score=6.0,
            median_score=5.0,
            lowest_score=4.0,
        )
    )
    session.commit()

    stored = session.get(Challenge, 42)
    assert stored is not None
    assert stored.voting_end == date(2004, 1, 14)


class TestMemberNameIsNeverNull:
    """members.name is NOT NULL, and blank names are deliberately not written."""

    def test_a_member_with_no_known_name_still_inserts(self, session):
        from dpc.parse.types import MemberRecord
        from dpc.scrape.store import upsert_member

        # The photographer of an image whose profile could not be parsed: the
        # crawler knows the id and nothing else. This used to violate NOT NULL,
        # because the "don't overwrite a name with a blank" guard also skipped
        # setting it on insert.
        member = upsert_member(session, MemberRecord(id=4242, name="", join_date=None))
        session.commit()

        assert member.name == ""
        assert session.get(Member, 4242) is not None

    def test_a_later_real_name_replaces_the_blank(self, session):
        from dpc.parse.types import MemberRecord
        from dpc.scrape.store import upsert_member

        upsert_member(session, MemberRecord(id=4242, name="", join_date=None))
        upsert_member(session, MemberRecord(id=4242, name="realname", join_date=None))
        session.commit()

        assert session.get(Member, 4242).name == "realname"

    def test_a_blank_never_overwrites_a_known_name(self, session):
        from dpc.parse.types import MemberRecord
        from dpc.scrape.store import upsert_member

        upsert_member(session, MemberRecord(id=4242, name="realname", join_date=None))
        upsert_member(session, MemberRecord(id=4242, name="", join_date=None))
        session.commit()

        assert session.get(Member, 4242).name == "realname"
