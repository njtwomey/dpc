"""Running Alembic migrations from code.

Real databases are created and evolved by migrations, so the schema has a
history. ``create_all`` remains for tests, where an in-memory database is built
from the models directly and speed matters more than provenance.
"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from dpc.config import PROJECT_ROOT

ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"


def _config(database_url: str) -> Config:
    config = Config(ALEMBIC_INI)
    config.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def upgrade(database_url: str, revision: str = "head") -> None:
    """Bring the database up to ``revision``, creating it if it does not exist."""
    url_path = database_url.removeprefix("sqlite+pysqlite:///").removeprefix("sqlite:///")
    if url_path != database_url:
        Path(url_path).parent.mkdir(parents=True, exist_ok=True)
    command.upgrade(_config(database_url), revision)


def current(database_url: str) -> None:
    command.current(_config(database_url), verbose=True)
