from __future__ import annotations

from datetime import date

from dpc.db.health import FABRICATED_DATE_THRESHOLD, check
from dpc.db.models import Challenge, Image, Member


def _challenge(session, challenge_id: int, submissions: int) -> None:
    session.add(
        Challenge(
            id=challenge_id,
            name=f"C{challenge_id}",
            description="",
            submission_start=date(2004, 1, 1),
            submission_end=date(2004, 1, 7),
            voting_start=date(2004, 1, 8),
            voting_end=date(2004, 1, 14),
            num_submissions=submissions,
            num_disqualifications=0,
            num_votes=0,
            num_comments=0,
            average_score=5.0,
            highest_score=6.0,
            median_score=5.0,
            lowest_score=4.0,
        )
    )


class TestCleanDatabase:
    def test_an_empty_database_is_healthy(self, session):
        health = check(session)
        assert health.ok
        assert health.integrity == []
        assert health.incomplete == []
        assert health.inherited == []


class TestIncompleteChallenges:
    def test_a_partly_scraped_challenge_is_reported(self, session):
        session.add(Member(id=1, name="p", join_date=date(2004, 1, 1)))
        _challenge(session, 100, submissions=10)
        session.add(Image(id=1, challenge_id=100, photographer_id=1, name="x", votes=[]))
        session.commit()

        health = check(session)
        assert [f.name for f in health.incomplete] == ["challenges missing images"]
        assert health.incomplete[0].count == 1

    def test_missing_data_does_not_fail_the_check(self, session):
        # It is something to go and fetch, not a sign the archive is broken.
        session.add(Member(id=1, name="p", join_date=date(2004, 1, 1)))
        _challenge(session, 100, submissions=10)
        session.add(Image(id=1, challenge_id=100, photographer_id=1, name="x", votes=[]))
        session.commit()

        assert check(session).ok

    def test_a_challenge_with_no_images_yet_is_not_incomplete(self, session):
        # Nothing fetched at all is a challenge not yet crawled, not a gap.
        _challenge(session, 100, submissions=10)
        session.commit()
        assert check(session).incomplete == []

    def test_a_fully_scraped_challenge_is_silent(self, session):
        session.add(Member(id=1, name="p", join_date=date(2004, 1, 1)))
        _challenge(session, 100, submissions=2)
        session.add(Image(id=1, challenge_id=100, photographer_id=1, name="x", votes=[]))
        session.add(Image(id=2, challenge_id=100, photographer_id=1, name="y", votes=[]))
        session.commit()
        assert check(session).incomplete == []


class TestInheritedArtefacts:
    def test_a_shared_join_date_is_reported_as_fabricated(self, session):
        # The old scraper stamped cancelled members with the day it ran.
        for i in range(FABRICATED_DATE_THRESHOLD):
            session.add(Member(id=i + 1, name=f"m{i}", join_date=date(2020, 10, 10)))
        session.commit()

        names = [f.name for f in check(session).inherited]
        assert "members with a fabricated join date" in names

    def test_a_few_members_sharing_a_date_is_just_a_coincidence(self, session):
        for i in range(3):
            session.add(Member(id=i + 1, name=f"m{i}", join_date=date(2020, 10, 10)))
        session.commit()
        assert check(session).inherited == []

    def test_a_nameless_member_is_reported(self, session):
        session.add(Member(id=1, name="", join_date=None))
        session.commit()
        assert [f.name for f in check(session).inherited] == ["members with no name"]

    def test_a_cancelled_member_may_legitimately_have_no_name(self, session):
        # The profile hides it; that is honest rather than missing.
        session.add(Member(id=1, name="", join_date=None, cancelled=True))
        session.commit()
        assert check(session).inherited == []
