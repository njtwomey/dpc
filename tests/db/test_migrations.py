"""The migration history must produce exactly the schema the models describe."""

from __future__ import annotations

import subprocess
import sys

import pytest
from sqlalchemy import inspect

from dpc.db.migrate import upgrade
from dpc.db.models import Base
from dpc.db.session import create_db_engine

pytestmark = pytest.mark.slow


@pytest.fixture
def migrated(tmp_path):
    url = f"sqlite+pysqlite:///{tmp_path / 'migrated.sqlite'}"
    upgrade(url)
    engine = create_db_engine(url)
    yield engine, url
    engine.dispose()


def test_creates_every_table(migrated):
    engine, _ = migrated
    tables = set(inspect(engine).get_table_names())
    assert set(Base.metadata.tables) <= tables


def test_stamps_a_version(migrated):
    engine, _ = migrated
    assert "alembic_version" in inspect(engine).get_table_names()


def test_migrations_and_models_have_not_drifted(migrated, tmp_path):
    """`alembic check` fails if the models describe something migrations do not."""
    _, url = migrated
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "check"],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
        env={**__import__("os").environ, "DPC_DATABASE_URL": url},
    )
    assert "No new upgrade operations detected" in result.stdout, result.stdout + result.stderr


def test_is_idempotent(migrated):
    _, url = migrated
    upgrade(url)  # running it again must not raise
