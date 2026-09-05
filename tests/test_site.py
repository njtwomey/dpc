"""Integration tests for the Hugo site.

Asset URLs are built twice: by ``dpc.export.urls`` in Python and by
``site/layouts/partials/urls/*.html`` in Go templates. The export deliberately
ships ids rather than URLs, so that duplication is the price -- these tests pin
the two implementations together so they cannot drift apart silently.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pytest

from dpc.awards.catalog import AwardCatalog
from dpc.awards.service import find_grants, sync_catalog
from dpc.db import Challenge, Comment, Image, Member, create_all, create_db_engine
from dpc.db.session import create_session_factory
from dpc.export.build import build_site_data
from dpc.export.urls import image_thumb_url, image_url, member_thumb_url
from dpc.export.writer import write_site_data

REPO_ROOT = Path(__file__).resolve().parents[1]
SITE = REPO_ROOT / "site"

CHALLENGE_ID = 1303
IMAGE_ID = 921974
MEMBER_ID = 75618

pytestmark = pytest.mark.slow

hugo = shutil.which("hugo")
requires_hugo = pytest.mark.skipif(hugo is None, reason="hugo is not installed")

CATALOG = AwardCatalog.model_validate(
    {
        "awarders": [
            {
                "name": "posthumous",
                "user_id": 50695,
                "awards": [
                    {
                        "name": "Posthumous Blue",
                        "description": "The blue one.",
                        "image": "blue.jpg",
                        "markers": ["bluepost"],
                    }
                ],
            }
        ]
    }
)


@pytest.fixture(scope="module")
def built_site(tmp_path_factory) -> Path:
    """Export a one-image dataset and run a real Hugo build over it."""
    if hugo is None:
        pytest.skip("hugo is not installed")

    workdir = tmp_path_factory.mktemp("site")
    target = workdir / "site"
    shutil.copytree(
        SITE, target, ignore=shutil.ignore_patterns("public", "resources", ".hugo_build.lock")
    )

    engine = create_db_engine(f"sqlite+pysqlite:///{workdir / 'db.sqlite'}")
    create_all(engine)
    session = create_session_factory(engine)()

    session.add(Member(id=MEMBER_ID, name="odriew", join_date=date(2004, 1, 1)))
    session.add(Member(id=50695, name="posthumous", join_date=date(2003, 1, 1)))
    session.add(
        Challenge(
            id=CHALLENGE_ID,
            name="Posthumous Ribbon",
            description="",
            submission_start=date(2004, 1, 1),
            submission_end=date(2004, 1, 7),
            voting_start=date(2004, 1, 8),
            voting_end=date(2004, 1, 14),
            num_submissions=1,
            num_disqualifications=0,
            num_votes=10,
            num_comments=1,
            average_score=5.0,
            highest_score=8.0,
            median_score=5.0,
            lowest_score=2.0,
        )
    )
    session.add(
        Image(
            id=IMAGE_ID,
            challenge_id=CHALLENGE_ID,
            photographer_id=MEMBER_ID,
            name="Disconnect",
            votes=[1] * 10,
            disqualified=False,
        )
    )
    session.commit()
    session.add(
        Comment(
            id=900,
            image_id=IMAGE_ID,
            commenter_id=50695,
            raw_comment="<td>bluepost</td>",
            comment="x",
            date=datetime(2004, 1, 15, 12, 0),
        )
    )
    session.commit()
    sync_catalog(session, CATALOG)
    find_grants(session, CATALOG)
    session.commit()

    write_site_data(build_site_data(session, CATALOG), target / "data" / "dpc")
    session.close()
    engine.dispose()

    result = subprocess.run(  # noqa: S603
        [hugo, "--logLevel", "warn", "--cleanDestinationDir"],
        cwd=target,
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    assert result.returncode == 0, f"hugo failed:\n{result.stdout}\n{result.stderr}"
    built: Path = target / "public"
    return built


@requires_hugo
class TestBuild:
    def test_produces_the_expected_pages(self, built_site):
        for page in [
            "index.html",
            "awarders/index.html",
            "awarders/posthumous/index.html",
            "awarders/posthumous/posthumous-blue/index.html",
            "challenges/index.html",
            "challenges/posthumous-ribbon/index.html",
            "recipients/index.html",
            "recipients/odriew/index.html",
        ]:
            assert (built_site / page).is_file(), f"missing {page}"

    def test_no_template_formatting_errors_leaked(self, built_site):
        for page in built_site.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            assert "%!d(" not in text, f"unformatted number in {page}"
            assert "%!s(" not in text, f"unformatted string in {page}"
            assert "ZgotmplZ" not in text, f"unsafe URL stripped by Go in {page}"


@pytest.fixture(scope="module")
def gallery(built_site: Path) -> str:
    page: str = (
        built_site / "awarders" / "posthumous" / "posthumous-blue" / "index.html"
    ).read_text(encoding="utf-8")
    return page


@pytest.fixture(scope="module")
def exported(built_site: Path) -> dict[str, Any]:
    source = built_site.parent / "data" / "dpc"
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in source.glob("*.json")}


@requires_hugo
class TestUrlsMatchThePythonImplementation:
    """The two URL builders must agree exactly."""

    def test_full_size_image_url(self, gallery):
        assert image_url(CHALLENGE_ID, IMAGE_ID) in gallery

    def test_thumbnail_url(self, gallery):
        assert image_thumb_url(CHALLENGE_ID, IMAGE_ID) in gallery

    def test_member_thumbnail_url(self, built_site):
        page = (built_site / "recipients" / "odriew" / "index.html").read_text(encoding="utf-8")
        assert member_thumb_url(MEMBER_ID) in page

    def test_links_back_to_dpchallenge(self, gallery):
        assert f"https://www.dpchallenge.com/image.php?IMAGE_ID={IMAGE_ID}" in gallery
        assert f"https://www.dpchallenge.com/profile.php?USER_ID={MEMBER_ID}" in gallery
        assert (
            f"https://www.dpchallenge.com/challenge_results.php?CHALLENGE_ID={CHALLENGE_ID}"
            in gallery
        )


@requires_hugo
class TestContentAdaptersCoverTheData:
    """Every row in the export must become a page, with nothing left over."""

    def test_one_page_per_challenge(self, built_site, exported):
        for challenge in exported["challenges"]:
            assert (built_site / "challenges" / challenge["slug"] / "index.html").is_file()

    def test_one_page_per_recipient(self, built_site, exported):
        for recipient in exported["recipients"]:
            assert (built_site / "recipients" / recipient["slug"] / "index.html").is_file()

    def test_one_page_per_award_under_its_awarder(self, built_site, exported):
        for award in exported["awards"]:
            page = built_site / "awarders" / award["awarder_slug"] / award["slug"] / "index.html"
            assert page.is_file(), f"missing {page}"

    def test_the_gallery_shows_every_awarded_image(self, built_site, exported):
        award = exported["awards"][0]
        page = (
            built_site / "awarders" / award["awarder_slug"] / award["slug"] / "index.html"
        ).read_text(encoding="utf-8")
        assert page.count('class="column is-2"') == len(award["image_ids"])
