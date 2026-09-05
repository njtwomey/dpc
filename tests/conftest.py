from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "html"


@pytest.fixture(scope="session")
def html() -> Callable[[str], str]:
    """Read a fixture page, e.g. ``html("challenge/results.html")``."""

    def _read(name: str) -> str:
        return (FIXTURES / name).read_text(encoding="utf-8")

    return _read


@pytest.fixture(scope="session")
def html_bytes() -> Callable[[str], bytes]:
    def _read(name: str) -> bytes:
        return (FIXTURES / name).read_bytes()

    return _read


@pytest.fixture
def session():
    """A real SQLite database, in memory, with the full schema."""
    from dpc.db import create_all, create_db_engine, create_session_factory

    engine = create_db_engine("sqlite+pysqlite:///:memory:")
    create_all(engine)
    factory = create_session_factory(engine)
    with factory() as active:
        yield active
    engine.dispose()


@pytest.fixture
def image(session):
    """A challenge, a photographer and one scored image, already committed."""
    from datetime import date as _date

    from dpc.db import Challenge, Image, Member

    session.add(Member(id=1, name="photographer", join_date=_date(2004, 1, 1)))
    session.add(
        Challenge(
            id=100,
            name="Test Challenge",
            description="",
            submission_start=_date(2004, 1, 1),
            submission_end=_date(2004, 1, 7),
            voting_start=_date(2004, 1, 8),
            voting_end=_date(2004, 1, 14),
            num_submissions=10,
            num_disqualifications=0,
            num_votes=100,
            num_comments=5,
            average_score=5.0,
            highest_score=8.0,
            median_score=5.0,
            lowest_score=2.0,
        )
    )
    picture = Image(
        id=500,
        challenge_id=100,
        photographer_id=1,
        name="Disconnect",
        votes=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        disqualified=False,
        average_all=5.9432,
    )
    session.add(picture)
    session.commit()
    return picture
