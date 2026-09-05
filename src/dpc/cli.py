"""``dpc`` -- the command line entry point, built on pydantic-settings.

Every subcommand is a model, so its options are validated the same way the rest
of the configuration is, and each one is constructible in a test without going
near ``sys.argv``.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, CliApp, CliSubCommand, SettingsConfigDict
from rich.console import Console
from rich.table import Table

from dpc.awards.asigmatic import grant_asigmatics
from dpc.awards.catalog import AwardCatalog
from dpc.awards.service import find_grants, sync_catalog
from dpc.config import PROJECT_ROOT, Credentials, Settings
from dpc.db.migrate import upgrade
from dpc.db.session import create_db_engine, create_session_factory, session_scope
from dpc.export.build import build_site_data
from dpc.export.writer import write_site_data
from dpc.log import configure as configure_logging
from dpc.scrape.cache import HtmlCache
from dpc.scrape.client import DpcClient
from dpc.scrape.crawl import Crawler

console = Console()

DEFAULT_CATALOG = PROJECT_ROOT / "awards.yaml"


def _table(title: str, rows: list[tuple[str, object]]) -> Table:
    table = Table("metric", "count", title=title)
    for label, value in rows:
        table.add_row(label, str(value))
    return table


class _Command(BaseModel):
    """Shared plumbing for every subcommand.

    Flag style (``--images`` / ``--no-images``) is configured once on ``Cli``.
    """

    def settings(self) -> Settings:
        return Settings()


class DbInit(_Command):
    """Create or upgrade the database schema by running migrations."""

    revision: str = Field("head", description="Alembic revision to upgrade to.")

    def cli_cmd(self) -> None:
        settings = self.settings()
        upgrade(settings.database_url, self.revision)
        console.print(f"schema at [bold]{self.revision}[/bold]: {settings.database_url}")


class Scrape(_Command):
    """Fetch challenges, images, comments and members into the local database."""

    challenge: list[int] = Field(default_factory=list, description="Specific challenge ids.")
    from_history: bool = Field(False, description="Discover ids from challenge_history.php.")
    refresh: bool = Field(False, description="Ignore the HTML cache and refetch.")
    images: bool = Field(True, description="Follow image pages. --no-images for metadata only.")

    def cli_cmd(self) -> None:
        settings = self.settings()
        if not self.challenge and not self.from_history:
            console.print("[yellow]pass --challenge or --from-history[/yellow]")
            raise SystemExit(2)

        engine = create_db_engine(settings.database_url)
        factory = create_session_factory(engine)
        cache = HtmlCache(settings.cache_dir)

        with DpcClient(settings, Credentials()) as client:
            client.login()
            with session_scope(factory) as session:
                crawler = Crawler(client, session, cache, refresh=self.refresh)
                candidates = (
                    list(self.challenge)
                    if self.challenge
                    else list(crawler.challenge_ids_from_history())
                )
                pending = crawler.pending_challenge_ids(candidates)
                console.print(f"{len(pending)} of {len(candidates)} challenges to fetch")
                stats = crawler.crawl_challenges(pending, with_images=self.images)

        engine.dispose()
        console.print(
            _table(
                "scrape",
                [
                    ("challenges", stats.challenges),
                    ("images", stats.images),
                    ("comments", stats.comments),
                    ("skipped (invalid id)", stats.skipped_invalid),
                    ("skipped (still open)", stats.skipped_unfinished),
                    ("failures", len(stats.failures)),
                ],
            )
        )
        if stats.failures:
            console.print(f"[red]failed:[/red] {stats.failures}")


class Awards(_Command):
    """Sync the award catalogue and find the awards hiding in comments."""

    catalog: Path = Field(DEFAULT_CATALOG, description="Award catalogue YAML.")
    asigmatic: bool = Field(True, description="Also derive the Asigmatic award.")

    def cli_cmd(self) -> None:
        settings = self.settings()
        catalog = AwardCatalog.load(self.catalog)
        engine = create_db_engine(settings.database_url)
        factory = create_session_factory(engine)

        with session_scope(factory) as session:
            report = sync_catalog(session, catalog)
            granted = find_grants(session, catalog)
            derived = grant_asigmatics(session) if self.asigmatic else 0

        engine.dispose()
        console.print(
            _table(
                "awards",
                [
                    ("awards created", report.created),
                    ("awards updated", report.updated),
                    ("awards unchanged", report.unchanged),
                    ("grants from comments", granted),
                    ("grants derived (asigmatic)", derived),
                ],
            )
        )


class Export(_Command):
    """Write the JSON dataset the Hugo site builds from."""

    catalog: Path = Field(DEFAULT_CATALOG, description="Award catalogue YAML.")
    out: Path | None = Field(None, description="Destination. Defaults to <site>/data/dpc.")

    def cli_cmd(self) -> None:
        settings = self.settings()
        catalog = AwardCatalog.load(self.catalog)
        destination = self.out or settings.export_dir
        engine = create_db_engine(settings.database_url)
        factory = create_session_factory(engine)

        with session_scope(factory) as session:
            data = build_site_data(session, catalog)
            written = write_site_data(data, destination)

        engine.dispose()
        console.print(
            _table(
                f"export -> {destination}",
                [
                    ("awarders", data.meta.num_awarders),
                    ("awards", data.meta.num_awards),
                    ("challenges", data.meta.num_challenges),
                    ("recipients", data.meta.num_recipients),
                    ("images", data.meta.num_images),
                    ("grants", data.meta.num_grants),
                ],
            )
        )
        console.print(f"wrote {len(written)} files")


class Check(_Command):
    """Validate the award catalogue without touching the database."""

    catalog: Path = Field(DEFAULT_CATALOG, description="Award catalogue YAML.")

    def cli_cmd(self) -> None:
        catalog = AwardCatalog.load(self.catalog)
        console.print(
            f"[green]ok[/green] {len(catalog.awarders)} awarders, {len(catalog.pairs())} awards"
        )


class Cli(BaseSettings):
    """Scrape dpchallenge awards and build the gallery site's data."""

    model_config = SettingsConfigDict(
        cli_prog_name="dpc",
        cli_parse_args=True,
        cli_kebab_case=True,
        cli_implicit_flags=True,
        cli_use_class_docs_for_groups=True,
        env_prefix="DPC_",
        extra="ignore",
    )

    verbose: bool = Field(False, description="Debug logging.")

    db_init: CliSubCommand[DbInit]
    scrape: CliSubCommand[Scrape]
    awards: CliSubCommand[Awards]
    export: CliSubCommand[Export]
    check: CliSubCommand[Check]

    def cli_cmd(self) -> None:
        configure_logging(verbose=self.verbose)
        CliApp.run_subcommand(self)


def main() -> None:
    CliApp.run(Cli)


if __name__ == "__main__":
    main()
