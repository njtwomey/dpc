from __future__ import annotations

import json
from datetime import date, datetime

import pytest

from dpc.awards.catalog import AwardCatalog
from dpc.awards.service import find_grants, sync_catalog
from dpc.db.models import Challenge, Comment, Image, Member
from dpc.export.build import build_site_data
from dpc.export.model import SCHEMA_VERSION
from dpc.export.writer import FILENAMES, write_site_data

CATALOG = AwardCatalog.model_validate(
    {
        "awarders": [
            {
                "name": "posthumous",
                "user_id": 50695,
                "awards": [
                    {
                        "name": "Posthumous Blue",
                        "description": "blue one",
                        "image": "blue.jpg",
                        "markers": ["bluepost"],
                    },
                    {
                        "name": "Posthumous Red",
                        "description": "red one",
                        "image": "red.jpg",
                        "markers": ["redpost"],
                    },
                ],
            }
        ]
    }
)


@pytest.fixture
def populated(session):
    session.add(Member(id=1, name="odriew", join_date=date(2004, 1, 1)))
    session.add(Member(id=2, name="someone else", join_date=date(2004, 1, 1)))
    session.add(Member(id=3, name="   ", join_date=date(2004, 1, 1)))  # nameless
    session.add(Member(id=50695, name="posthumous", join_date=date(2003, 1, 1)))

    for challenge_id, end in ((100, date(2004, 1, 14)), (101, date(2005, 1, 14))):
        session.add(
            Challenge(
                id=challenge_id,
                name=f"Challenge {challenge_id}",
                description="",
                submission_start=date(2004, 1, 1),
                submission_end=date(2004, 1, 7),
                voting_start=date(2004, 1, 8),
                voting_end=end,
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

    images = [(500, 100, 1), (501, 100, 2), (502, 101, 1), (503, 101, 3)]
    for image_id, challenge_id, photographer_id in images:
        session.add(
            Image(
                id=image_id,
                challenge_id=challenge_id,
                photographer_id=photographer_id,
                name=f"Image {image_id}",
                votes=[1] * 10,
                disqualified=False,
            )
        )
    session.commit()

    comments = [
        (900, 500, "<td>bluepost</td>", datetime(2004, 1, 15, 12, 0)),
        (901, 501, "<td>redpost</td>", datetime(2004, 1, 16, 12, 0)),
        (902, 502, "<td>bluepost redpost</td>", datetime(2005, 1, 15, 12, 0)),
        (903, 503, "<td>bluepost</td>", datetime(2005, 1, 16, 12, 0)),
    ]
    for comment_id, image_id, html, when in comments:
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

    sync_catalog(session, CATALOG)
    find_grants(session, CATALOG)
    session.commit()
    return session


class TestMeta:
    def test_counts_line_up(self, populated):
        data = build_site_data(populated, CATALOG)

        assert data.meta.schema_version == SCHEMA_VERSION
        assert data.meta.num_grants == 5
        assert data.meta.num_awards == 2
        assert data.meta.num_awarders == 1
        assert data.meta.num_challenges == 2
        assert data.meta.num_images == 4


class TestAwards:
    def test_tallies_are_correct(self, populated):
        data = build_site_data(populated, CATALOG)
        blue = next(a for a in data.awards if a.slug == "posthumous-blue")

        assert blue.num_granted == 3
        # images 500 and 502 share photographer 1, so three grants but two people
        assert blue.num_recipients == 2
        assert blue.num_challenges == 2
        assert blue.awarder_name == "posthumous"
        assert blue.description == "blue one"

    def test_images_are_most_recent_first(self, populated):
        data = build_site_data(populated, CATALOG)
        blue = next(a for a in data.awards if a.slug == "posthumous-blue")
        assert blue.image_ids == [503, 502, 500]

    def test_awards_are_sorted_by_slug(self, populated):
        data = build_site_data(populated, CATALOG)
        assert [a.slug for a in data.awards] == ["posthumous-blue", "posthumous-red"]


class TestChallenges:
    def test_ordered_most_recent_first(self, populated):
        data = build_site_data(populated, CATALOG)
        assert [c.id for c in data.challenges] == [101, 100]

    def test_carries_the_date_voting_closed(self, populated):
        # The only chronology the site has: the list groups on it.
        data = build_site_data(populated, CATALOG)
        assert [c.ended for c in data.challenges] == ["2005-01-14", "2004-01-14"]

    def test_award_counts_are_most_common_first(self, populated):
        data = build_site_data(populated, CATALOG)
        recent = next(c for c in data.challenges if c.id == 101)
        assert recent.award_counts[0].slug == "posthumous-blue"
        assert recent.award_counts[0].count == 2

    def test_image_ids_are_deduplicated(self, populated):
        # Image 502 wins two awards; it must appear once.
        data = build_site_data(populated, CATALOG)
        recent = next(c for c in data.challenges if c.id == 101)
        assert sorted(recent.image_ids) == [502, 503]


class TestRecipients:
    def test_ordered_by_award_count_descending(self, populated):
        data = build_site_data(populated, CATALOG)
        assert [r.num_granted for r in data.recipients] == sorted(
            (r.num_granted for r in data.recipients), reverse=True
        )

    def test_nameless_members_are_excluded(self, populated):
        # Member 3 has a blank name; a card for them renders an empty link.
        data = build_site_data(populated, CATALOG)
        assert 3 not in {r.id for r in data.recipients}

    def test_distinct_award_and_challenge_counts(self, populated):
        data = build_site_data(populated, CATALOG)
        odriew = next(r for r in data.recipients if r.id == 1)
        assert odriew.num_granted == 3
        assert odriew.num_awards == 2
        assert odriew.num_challenges == 2


class TestImages:
    def test_keyed_by_string_id_for_hugo(self, populated):
        data = build_site_data(populated, CATALOG)
        assert "502" in data.images
        assert data.images["502"].challenge_id == 101

    def test_records_every_award_on_an_image(self, populated):
        data = build_site_data(populated, CATALOG)
        assert data.images["502"].awards == ["posthumous-blue", "posthumous-red"]


class TestWriter:
    def test_writes_one_file_per_collection(self, populated, tmp_path):
        written = write_site_data(build_site_data(populated, CATALOG), tmp_path)
        assert {p.stem for p in written} == set(FILENAMES)

    def test_output_is_valid_json(self, populated, tmp_path):
        write_site_data(build_site_data(populated, CATALOG), tmp_path)
        loaded = json.loads((tmp_path / "awards.json").read_text(encoding="utf-8"))
        assert loaded[0]["slug"] == "posthumous-blue"

    def test_re_export_is_byte_identical(self, populated, tmp_path):
        # An unchanged database must produce an empty git diff, so that a diff
        # genuinely means the data changed.
        first, second = tmp_path / "a", tmp_path / "b"
        write_site_data(build_site_data(populated, CATALOG), first)
        write_site_data(build_site_data(populated, CATALOG), second)

        for name in FILENAMES:
            assert (first / f"{name}.json").read_bytes() == (second / f"{name}.json").read_bytes()

    def test_files_end_with_a_newline(self, populated, tmp_path):
        write_site_data(build_site_data(populated, CATALOG), tmp_path)
        assert (tmp_path / "meta.json").read_text(encoding="utf-8").endswith("\n")

    def test_unicode_is_not_escaped(self, populated, tmp_path):
        populated.query(Challenge).filter_by(id=101).one().name = "Hidden Gem — Quiz"
        populated.commit()
        write_site_data(build_site_data(populated, CATALOG), tmp_path)

        raw = (tmp_path / "challenges.json").read_text(encoding="utf-8")
        assert "—" in raw
        assert "\\u2014" not in raw


class TestGrantsWithoutAComment:
    """comment_id is nullable, so the grants query must not inner-join Comment."""

    def test_a_comment_less_grant_still_reaches_the_export(self, populated):
        from dpc.db.models import Award, AwardGrant

        award = populated.query(Award).filter_by(slug="posthumous-blue").one()
        before = build_site_data(populated, CATALOG).meta.num_grants

        populated.add(
            AwardGrant(
                award_id=award.id,
                recipient_id=2,
                comment_id=None,
                image_id=501,
                challenge_id=100,
            )
        )
        populated.commit()

        assert build_site_data(populated, CATALOG).meta.num_grants == before + 1

    def test_it_is_dated_by_its_challenge(self, populated):
        from dpc.db.models import Award, AwardGrant

        award = populated.query(Award).filter_by(slug="posthumous-red").one()
        populated.add(
            AwardGrant(
                award_id=award.id,
                recipient_id=1,
                comment_id=None,
                image_id=500,
                challenge_id=100,
            )
        )
        populated.commit()

        red = next(
            a for a in build_site_data(populated, CATALOG).awards if a.slug == "posthumous-red"
        )
        assert 500 in red.image_ids


class TestOutputFormat:
    """One minified record per line: small, but still diffable per record."""

    def test_each_record_is_on_its_own_line(self, populated, tmp_path):
        write_site_data(build_site_data(populated, CATALOG), tmp_path)
        text = (tmp_path / "awards.json").read_text(encoding="utf-8")

        lines = text.splitlines()
        assert lines[0] == "["
        assert lines[-1] == "]"
        assert len(lines) == 2 + len(json.loads(text))

    def test_images_are_one_per_line_keyed_by_id(self, populated, tmp_path):
        write_site_data(build_site_data(populated, CATALOG), tmp_path)
        text = (tmp_path / "images.json").read_text(encoding="utf-8")

        lines = text.splitlines()
        assert lines[0] == "{"
        assert lines[-1] == "}"
        assert all(line.lstrip().startswith('"') for line in lines[1:-1])

    def test_records_carry_no_internal_padding(self, populated, tmp_path):
        write_site_data(build_site_data(populated, CATALOG), tmp_path)
        text = (tmp_path / "challenges.json").read_text(encoding="utf-8")
        assert '", "' not in text
        assert '": ' not in text

    def test_still_parses_and_stays_deterministic(self, populated, tmp_path):
        first, second = tmp_path / "a", tmp_path / "b"
        write_site_data(build_site_data(populated, CATALOG), first)
        write_site_data(build_site_data(populated, CATALOG), second)

        for name in FILENAMES:
            raw = (first / f"{name}.json").read_bytes()
            assert raw == (second / f"{name}.json").read_bytes()
            json.loads(raw)
