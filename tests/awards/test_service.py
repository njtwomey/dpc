from __future__ import annotations

from datetime import date, datetime

import pytest

from dpc.awards.catalog import AwardCatalog
from dpc.awards.service import find_grants, sync_catalog
from dpc.db.models import Award, AwardGrant, Challenge, Comment, Image, Member

CATALOG = AwardCatalog.model_validate(
    {
        "awarders": [
            {
                "name": "posthumous",
                "user_id": 50695,
                "awards": [
                    {
                        "name": "Posthumous Blue",
                        "description": "d",
                        "image": "i",
                        "markers": ["bluepost", "1077284"],
                    },
                    {
                        "name": "Posthumous Red",
                        "description": "d",
                        "image": "i",
                        "markers": ["redpost"],
                    },
                ],
            }
        ]
    }
)


@pytest.fixture
def world(session):
    """One challenge, one photographer, two images, and an awarder."""
    session.add(Member(id=1, name="photographer", join_date=date(2004, 1, 1)))
    session.add(Member(id=50695, name="posthumous", join_date=date(2003, 1, 1)))
    session.add(
        Challenge(
            id=100,
            name="Test Challenge",
            description="",
            submission_start=date(2004, 1, 1),
            submission_end=date(2004, 1, 7),
            voting_start=date(2004, 1, 8),
            voting_end=date(2004, 1, 14),
            num_submissions=2,
            num_disqualifications=0,
            num_votes=10,
            num_comments=2,
            average_score=5.0,
            highest_score=8.0,
            median_score=5.0,
            lowest_score=2.0,
        )
    )
    for image_id in (500, 501):
        session.add(
            Image(
                id=image_id,
                challenge_id=100,
                photographer_id=1,
                name=f"img{image_id}",
                votes=[1] * 10,
                disqualified=False,
            )
        )
    session.commit()
    return session


def _comment(session, comment_id, image_id, html, when=datetime(2004, 1, 15, 12, 0, 0)):
    session.add(
        Comment(
            id=comment_id,
            image_id=image_id,
            commenter_id=50695,
            raw_comment=html,
            comment="x",
            date=when,
        )
    )
    session.commit()


class TestSyncCatalog:
    def test_creates_awards(self, world):
        report = sync_catalog(world, CATALOG)
        world.commit()

        assert report.created == 2
        assert {a.slug for a in world.query(Award).all()} == {"posthumous-blue", "posthumous-red"}

    def test_second_run_changes_nothing(self, world):
        sync_catalog(world, CATALOG)
        world.commit()
        report = sync_catalog(world, CATALOG)
        world.commit()

        assert report.created == 0
        assert report.updated == 0
        assert report.unchanged == 2

    def test_edits_to_the_catalogue_actually_persist(self, world):
        # The regression this test exists for: the old builder called
        # award.update(**kwargs) on a peewee instance, which builds a query and
        # throws it away. Award metadata edits never reached the database.
        sync_catalog(world, CATALOG)
        world.commit()

        edited = CATALOG.model_copy(deep=True)
        revised = edited.model_dump()
        revised["awarders"][0]["awards"][0]["description"] = "a new description"
        report = sync_catalog(world, AwardCatalog.model_validate(revised))
        world.commit()

        assert report.updated == 1
        stored = world.query(Award).filter_by(slug="posthumous-blue").one()
        assert stored.description == "a new description"

    def test_marker_edits_persist_too(self, world):
        sync_catalog(world, CATALOG)
        world.commit()

        revised = CATALOG.model_dump()
        revised["awarders"][0]["awards"][0]["markers"] = ["bluepost", "1077284", "newmarker"]
        sync_catalog(world, AwardCatalog.model_validate(revised))
        world.commit()

        stored = world.query(Award).filter_by(slug="posthumous-blue").one()
        assert "newmarker" in stored.markers


class TestFindGrants:
    def test_grants_an_award_from_a_marker_in_the_comment_html(self, world):
        sync_catalog(world, CATALOG)
        _comment(world, 900, 500, '<td><img src="http://blackyak.com/dpc/bluepost.gif"></td>')

        assert find_grants(world, CATALOG) == 1
        world.commit()

        grant = world.query(AwardGrant).one()
        assert grant.image_id == 500
        assert grant.recipient_id == 1
        assert grant.challenge_id == 100
        assert grant.comment_id == 900

    def test_no_marker_no_grant(self, world):
        sync_catalog(world, CATALOG)
        _comment(world, 900, 500, "<td>Nice shot!</td>")
        assert find_grants(world, CATALOG) == 0

    def test_is_idempotent(self, world):
        sync_catalog(world, CATALOG)
        _comment(world, 900, 500, "<td>bluepost</td>")

        assert find_grants(world, CATALOG) == 1
        world.commit()
        assert find_grants(world, CATALOG) == 0
        world.commit()
        assert world.query(AwardGrant).count() == 1

    def test_one_award_reaches_an_image_only_once(self, world):
        # Two comments by the same awarder on the same image, both carrying the
        # same award. The old code recomputed "already awarded" once up front,
        # so a within-run repeat slipped through.
        sync_catalog(world, CATALOG)
        _comment(world, 900, 500, "<td>bluepost</td>", datetime(2004, 1, 15, 12, 0, 0))
        _comment(world, 901, 500, "<td>bluepost</td>", datetime(2004, 1, 16, 12, 0, 0))

        assert find_grants(world, CATALOG) == 1
        world.commit()
        assert world.query(AwardGrant).count() == 1

    def test_keeps_the_earliest_comment_when_there_are_several(self, world):
        sync_catalog(world, CATALOG)
        _comment(world, 901, 500, "<td>bluepost</td>", datetime(2004, 1, 16, 12, 0, 0))
        _comment(world, 900, 500, "<td>bluepost</td>", datetime(2004, 1, 15, 12, 0, 0))

        find_grants(world, CATALOG)
        world.commit()
        assert world.query(AwardGrant).one().comment_id == 900

    def test_two_different_awards_can_reach_one_image(self, world):
        sync_catalog(world, CATALOG)
        _comment(world, 900, 500, "<td>bluepost redpost</td>")

        assert find_grants(world, CATALOG) == 2
        world.commit()
        assert world.query(AwardGrant).count() == 2

    def test_only_the_awarders_own_comments_count(self, world):
        sync_catalog(world, CATALOG)
        world.add(Member(id=777, name="impostor", join_date=date(2004, 1, 1)))
        world.add(
            Comment(
                id=902,
                image_id=500,
                commenter_id=777,
                raw_comment="<td>bluepost</td>",
                comment="x",
                date=datetime(2004, 1, 15, 12, 0, 0),
            )
        )
        world.commit()

        assert find_grants(world, CATALOG) == 0
