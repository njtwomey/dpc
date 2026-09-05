"""Integration tests for the site build.

The site is a React app prerendered to static HTML: one file per URL, with a
single client island for the image viewer. Asset URLs are built twice -- by
``dpc.export.urls`` in Python and by ``site/src/lib/urls.ts`` in TypeScript --
because the export ships ids rather than URLs. These tests pin the two together
so they cannot drift apart silently.
"""

from __future__ import annotations

import json
import os
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

npm = shutil.which("npm")
requires_node = pytest.mark.skipif(
    npm is None or not (SITE / "node_modules").is_dir(),
    reason="needs npm and `npm ci` in site/",
)

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


def _seed(session) -> None:
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


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> Path:
    """Export a one-image dataset and run the real site build over it."""
    if npm is None or not (SITE / "node_modules").is_dir():
        pytest.skip("needs npm and `npm ci` in site/")

    workdir = tmp_path_factory.mktemp("site")
    engine = create_db_engine(f"sqlite+pysqlite:///{workdir / 'db.sqlite'}")
    create_all(engine)
    session = create_session_factory(engine)()
    _seed(session)
    data = build_site_data(session, CATALOG)
    session.close()
    engine.dispose()

    # Build in place against a swapped-in dataset, then restore. Copying the
    # whole site would mean copying node_modules.
    live = SITE / "data" / "dpc"
    backup = workdir / "data-backup"
    shutil.copytree(live, backup)
    try:
        for stale in live.glob("*.json"):
            stale.unlink()
        write_site_data(data, live)
        result = subprocess.run(  # noqa: S603
            [npm, "run", "build"],
            cwd=SITE,
            capture_output=True,
            text=True,
            check=False,
            timeout=900,
            env={**os.environ, "SITE_BASE": "/dpc/"},
        )
        assert result.returncode == 0, f"build failed:\n{result.stdout}\n{result.stderr}"
        out = workdir / "dist"
        shutil.copytree(SITE / "dist", out)
        assert out.is_dir()
    finally:
        for stale in live.glob("*.json"):
            stale.unlink()
        for restored in backup.glob("*.json"):
            shutil.copy(restored, live)

    return Path(out)


@requires_node
class TestBuild:
    def test_produces_a_file_per_url(self, built: Path) -> None:
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
            assert (built / page).is_file(), f"missing {page}"

    def test_pages_render_without_javascript(self, built: Path) -> None:
        # Prerendered, not a client-side app: the gallery is in the markup.
        page = (built / "awarders" / "posthumous" / "posthumous-blue" / "index.html").read_text(
            encoding="utf-8"
        )
        assert "data-image-index" in page
        assert "Disconnect" in page

    def test_the_client_bundle_stays_small(self, built: Path) -> None:
        # Only the viewer ships. Importing lib/dpc here would drag the whole
        # image dataset into every page, as it once did at 1.9 MB.
        total = sum(f.stat().st_size for f in (built / "assets").glob("*.js"))
        assert total < 600_000, f"client bundle is {total:,} bytes"


@requires_node
class TestBasePath:
    """Pages serves the site under /dpc/, so every internal URL needs it."""

    def test_every_internal_link_carries_the_base(self, built: Path) -> None:
        import re

        page = (built / "index.html").read_text(encoding="utf-8")
        refs = set(re.findall(r'(?:href|src)="(/[^"]*)"', page))
        assert refs, "no absolute internal references at all"
        assert all(r.startswith("/dpc/") for r in refs), sorted(
            r for r in refs if not r.startswith("/dpc/")
        )

    def test_assets_are_prefixed_too(self, built: Path) -> None:
        page = (built / "index.html").read_text(encoding="utf-8")
        assert '"/dpc/assets/' in page


@pytest.fixture(scope="module")
def gallery(built: Path) -> str:
    return (built / "awarders" / "posthumous" / "posthumous-blue" / "index.html").read_text(
        encoding="utf-8"
    )


@requires_node
class TestUrlsMatchThePythonImplementation:
    def test_thumbnail_url(self, gallery: str) -> None:
        assert image_thumb_url(CHALLENGE_ID, IMAGE_ID) in gallery

    def test_full_size_url_is_embedded_for_the_viewer(self, built: Path) -> None:
        # The viewer builds it from ids at runtime, so the ids must be present.
        page = (built / "awarders" / "posthumous" / "posthumous-blue" / "index.html").read_text(
            encoding="utf-8"
        )
        payload: list[dict[str, Any]] = json.loads(
            page.split('data-gallery-payload="">')[1].split("</script>")[0]
        )["images"]
        assert payload[0]["id"] == IMAGE_ID
        assert payload[0]["challenge_id"] == CHALLENGE_ID
        assert image_url(CHALLENGE_ID, IMAGE_ID).endswith(f"{IMAGE_ID}.jpg")

    def test_member_thumbnail_url(self, built: Path) -> None:
        page = (built / "recipients" / "odriew" / "index.html").read_text(encoding="utf-8")
        assert member_thumb_url(MEMBER_ID) in page

    def test_links_back_to_dpchallenge(self, gallery: str) -> None:
        assert f"https://www.dpchallenge.com/image.php?IMAGE_ID={IMAGE_ID}" in gallery
        assert f"https://www.dpchallenge.com/profile.php?USER_ID={MEMBER_ID}" in gallery
