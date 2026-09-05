"""Runtime configuration.

Two separate settings objects on purpose:

``Settings`` holds paths and the database URL and is always loadable, so the
export and site-build commands never need credentials in the environment.
``Credentials`` holds the dpchallenge login and is constructed only by the
scraper. The password is a :class:`~pydantic.SecretStr`, so it never appears in
a repr, a log record, or a traceback.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_CONFIG = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    env_prefix="DPC_",
    extra="ignore",
)


class Settings(BaseSettings):
    """Non-secret configuration. Safe to construct anywhere."""

    model_config = _CONFIG

    database_url: str = f"sqlite+pysqlite:///{PROJECT_ROOT / 'dpc.sqlite'}"
    """SQLAlchemy URL. Defaults to a SQLite file at the repository root."""

    cache_dir: Path = PROJECT_ROOT / "downloaded"
    """Where fetched HTML is cached, so re-runs and fixtures are cheap."""

    site_dir: Path = PROJECT_ROOT / "site"
    """Root of the Hugo site. ``dpc export`` writes into ``site_dir/data/dpc``."""

    request_timeout: float = 30.0
    request_delay: float = 1.0
    """Seconds to wait between requests. Be polite to the origin."""

    max_retries: int = 5

    @property
    def export_dir(self) -> Path:
        return self.site_dir / "data" / "dpc"


class Credentials(BaseSettings):
    """dpchallenge login. Constructed only when the scraper actually needs it."""

    model_config = _CONFIG

    username: str
    password: SecretStr

    def as_login_form(self) -> dict[str, str]:
        """Build the login POST body.

        ``SAVE_PASSWORD`` and ``REDIRECT`` are form constants, not secrets --
        they used to live alongside the real password in login_details.json.
        """
        return {
            "USERNAME": self.username,
            "PASSWORD": self.password.get_secret_value(),
            "SAVE_PASSWORD": "1",
            "REDIRECT": "/index.php",
        }
