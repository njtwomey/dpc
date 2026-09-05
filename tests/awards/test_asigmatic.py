from __future__ import annotations

from datetime import date

import pytest

from dpc.awards.asigmatic import grant_asigmatics, most_divisive, vote_spread
from dpc.db.models import Award, AwardGrant, Challenge, Comment, Image, Member


class TestVoteSpread:
    def test_unanimous_votes_have_no_spread(self):
        votes = [0, 0, 0, 0, 10, 0, 0, 0, 0, 0]  # ten voters all gave 5
        assert vote_spread(votes) == 0.0

    def test_split_crowd_has_a_large_spread(self):
        polarised = [5, 0, 0, 0, 0, 0, 0, 0, 0, 5]  # half 1s, half 10s
        middling = [0, 0, 0, 5, 0, 0, 5, 0, 0, 0]  # half 4s, half 7s
        assert vote_spread(polarised) > vote_spread(middling)

    def test_polarised_spread_is_exact(self):
        # Half at 1, half at 10: population sd is 4.5.
        assert vote_spread([5, 0, 0, 0, 0, 0, 0, 0, 0, 5]) == pytest.approx(4.5)

    @pytest.mark.parametrize("votes", [[0] * 10, [1] + [0] * 9])
    def test_too_few_votes_is_zero_not_an_error(self, votes):
        assert vote_spread(votes) == 0.0


@pytest.fixture
def challenge(session):
    session.add(Member(id=1, name="a", join_date=date(2004, 1, 1)))
    session.add(Member(id=2, name="b", join_date=date(2004, 1, 1)))
    session.add(Member(id=117474, name="NiallOTuama", join_date=date(2004, 1, 1)))
    session.add(
        Challenge(
            id=100,
            name="C",
            description="",
            submission_start=date(2004, 1, 1),
            submission_end=date(2004, 1, 7),
            voting_start=date(2004, 1, 8),
            voting_end=date(2004, 1, 14),
            num_submissions=2,
            num_disqualifications=0,
            num_votes=10,
            num_comments=0,
            average_score=5.0,
            highest_score=8.0,
            median_score=5.0,
            lowest_score=2.0,
        )
    )
    session.add(Award(id=1, awarder_id=117474, name="Asigmatic", slug="asigmatic", markers=["x"]))
    session.commit()
    return session


def _image(session, image_id, photographer_id, votes, *, disqualified=False):
    session.add(
        Image(
            id=image_id,
            challenge_id=100,
            photographer_id=photographer_id,
            name=f"img{image_id}",
            votes=votes,
            disqualified=disqualified,
        )
    )
    session.commit()


class TestMostDivisive:
    def test_picks_the_widest_spread(self, challenge):
        _image(challenge, 500, 1, [0, 0, 0, 0, 10, 0, 0, 0, 0, 0])
        _image(challenge, 501, 2, [5, 0, 0, 0, 0, 0, 0, 0, 0, 5])

        winner = most_divisive(challenge, 100)
        assert winner is not None
        assert winner.id == 501

    def test_skips_disqualified_images(self, challenge):
        _image(challenge, 500, 1, [0, 0, 0, 0, 10, 0, 0, 0, 0, 0])
        _image(challenge, 501, 2, [5, 0, 0, 0, 0, 0, 0, 0, 0, 5], disqualified=True)

        winner = most_divisive(challenge, 100)
        assert winner is not None
        assert winner.id == 500

    def test_skips_images_with_no_votes(self, challenge):
        _image(challenge, 500, 1, [0] * 10)
        _image(challenge, 501, 2, [0, 0, 0, 0, 10, 0, 0, 0, 0, 0])

        winner = most_divisive(challenge, 100)
        assert winner is not None
        assert winner.id == 501

    def test_returns_none_when_nothing_is_eligible(self, challenge):
        _image(challenge, 500, 1, [0] * 10)
        assert most_divisive(challenge, 100) is None

    def test_ties_break_on_the_lowest_image_id(self, challenge):
        same = [5, 0, 0, 0, 0, 0, 0, 0, 0, 5]
        _image(challenge, 501, 1, same)
        _image(challenge, 500, 2, same)

        winner = most_divisive(challenge, 100)
        assert winner is not None
        assert winner.id == 500


class TestGrantAsigmatics:
    def test_grants_one_per_challenge(self, challenge):
        _image(challenge, 500, 1, [0, 0, 0, 0, 10, 0, 0, 0, 0, 0])
        _image(challenge, 501, 2, [5, 0, 0, 0, 0, 0, 0, 0, 0, 5])

        assert grant_asigmatics(challenge) == 1
        challenge.commit()

        grant = challenge.query(AwardGrant).one()
        assert grant.image_id == 501
        assert grant.recipient_id == 2

    def test_derived_grant_has_no_comment(self, challenge):
        # The old code minted a fake Comment whose primary key was the challenge
        # id, colliding with real comment ids.
        _image(challenge, 500, 1, [5, 0, 0, 0, 0, 0, 0, 0, 0, 5])
        grant_asigmatics(challenge)
        challenge.commit()

        assert challenge.query(AwardGrant).one().comment_id is None
        assert challenge.query(Comment).count() == 0

    def test_is_idempotent(self, challenge):
        _image(challenge, 500, 1, [5, 0, 0, 0, 0, 0, 0, 0, 0, 5])

        assert grant_asigmatics(challenge) == 1
        challenge.commit()
        assert grant_asigmatics(challenge) == 0
        challenge.commit()
        assert challenge.query(AwardGrant).count() == 1

    def test_no_award_in_catalogue_is_a_no_op(self, session):
        assert grant_asigmatics(session) == 0
