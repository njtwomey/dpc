"""``dpc`` -- the command line entry point, built on pydantic-settings.

Every subcommand is a model, so its options are validated the same way the rest
of the configuration is, and each one is constructible in a test without going
near ``sys.argv``.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, CliApp, CliSubCommand, SettingsConfigDict
from rich.console import Console
from rich.table import Table
from sqlalchemy import text
from sqlalchemy.orm import Session

from dpc.awards.catalog import AwardCatalog
from dpc.awards.service import find_grants, sync_catalog
from dpc.config import PROJECT_ROOT, Credentials, Settings, env_file_permission_warning
from dpc.db.health import FABRICATED_DATE_THRESHOLD
from dpc.db.health import check as check_health
from dpc.db.migrate import upgrade
from dpc.db.session import create_db_engine, create_session_factory, session_scope
from dpc.export.build import build_site_data
from dpc.export.writer import write_site_data
from dpc.log import configure as configure_logging
from dpc.scrape.cache import HtmlCache
from dpc.scrape.client import DpcClient
from dpc.scrape.crawl import Crawler

console = Console()

DEFAULT_CATALOG = PROJECT_ROOT / "config" / "awards.yaml"


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
    incomplete: bool = Field(
        False, description="Refetch challenges holding only some of their images."
    )
    refresh: bool = Field(False, description="Ignore the HTML cache and refetch.")
    images: bool = Field(True, description="Follow image pages. --no-images for metadata only.")

    def cli_cmd(self) -> None:
        settings = self.settings()
        if not self.challenge and not self.from_history and not self.incomplete:
            console.print("[yellow]pass --challenge, --from-history or --incomplete[/yellow]")
            raise SystemExit(2)

        engine = create_db_engine(settings.database_url)
        factory = create_session_factory(engine)
        cache = HtmlCache(settings.cache_dir)

        with DpcClient(settings, Credentials()) as client:
            client.login()
            with session_scope(factory) as session:
                crawler = Crawler(client, session, cache, refresh=self.refresh)
                if self.challenge:
                    candidates = list(self.challenge)
                elif self.incomplete:
                    candidates = _incomplete_challenge_ids(session)
                else:
                    candidates = list(crawler.challenge_ids_from_history())

                # Explicit ids and --incomplete both mean "do these", so the
                # already-stored filter would defeat the point.
                pending = (
                    candidates
                    if (self.challenge or self.incomplete)
                    else crawler.pending_challenge_ids(candidates)
                )
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


def _incomplete_challenge_ids(session: Session) -> list[int]:
    """Challenges holding some but not all of their images."""
    rows = session.execute(
        text(
            # Short, not merely different: the results page also lists
            # disqualified entries, so more images than num_submissions is
            # normal. See dpc.db.health.INCOMPLETE_CHALLENGES.
            "SELECT c.id FROM challenges c WHERE c.num_submissions > 0 AND "
            "(SELECT COUNT(*) FROM images i WHERE i.challenge_id = c.id) "
            "BETWEEN 1 AND c.num_submissions - 1 ORDER BY c.id"
        )
    )
    return [int(row[0]) for row in rows]


class Awards(_Command):
    """Sync the award catalogue and find the awards hiding in comments."""

    catalog: Path = Field(DEFAULT_CATALOG, description="Award catalogue YAML.")

    def cli_cmd(self) -> None:
        settings = self.settings()
        catalog = AwardCatalog.load(self.catalog)
        engine = create_db_engine(settings.database_url)
        factory = create_session_factory(engine)

        with session_scope(factory) as session:
            report = sync_catalog(session, catalog)
            granted = find_grants(session, catalog)

        engine.dispose()
        console.print(
            _table(
                "awards",
                [
                    ("awards created", report.created),
                    ("awards updated", report.updated),
                    ("awards unchanged", report.unchanged),
                    ("grants from comments", granted),
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


class Verify(_Command):
    """Check the archive for inconsistencies."""

    def cli_cmd(self) -> None:
        settings = self.settings()
        engine = create_db_engine(settings.database_url)
        factory = create_session_factory(engine)

        with session_scope(factory) as session:
            health = check_health(session)
        engine.dispose()

        if health.incomplete:
            table = Table("gap", "count", "meaning", title="missing data")
            for finding in health.incomplete:
                table.add_row(finding.name, f"{finding.count:,}", finding.detail)
            console.print(table)

        if health.integrity:
            table = Table("problem", "count", "meaning", title="integrity")
            for finding in health.integrity:
                table.add_row(finding.name, f"{finding.count:,}", finding.detail)
            console.print(table)
        else:
            console.print("[green]integrity: nothing contradicts itself[/green]")

        if health.inherited:
            table = Table("artefact", "count", "meaning", title="inherited from the old scraper")
            for finding in health.inherited:
                table.add_row(finding.name, f"{finding.count:,}", finding.detail)
            console.print(table)

        if not health.ok:
            raise SystemExit(1)


class RefreshMembers(_Command):
    """Refetch member profiles the old scraper never read properly."""

    ids: list[int] = Field(default_factory=list, description="Specific member ids.")
    blank_names: bool = Field(True, description="Members stored with no name.")
    fabricated_dates: bool = Field(
        False, description="Members sharing a join date with many others (a scrape date)."
    )
    limit: int = Field(0, description="Stop after this many. 0 means no limit.")

    def cli_cmd(self) -> None:
        settings = self.settings()
        engine = create_db_engine(settings.database_url)
        factory = create_session_factory(engine)
        cache = HtmlCache(settings.cache_dir)

        with session_scope(factory) as session:
            targets = self._targets(session)
            if not targets:
                console.print("nothing to refresh")
                return

            console.print(f"refreshing {len(targets):,} member profiles")
            with DpcClient(settings, Credentials()) as client:
                client.login()
                crawler = Crawler(client, session, cache, refresh=True)
                updated = crawler.refresh_members(targets)

        engine.dispose()
        console.print(
            _table("refresh-members", [("requested", len(targets)), ("updated", updated)])
        )

    def _targets(self, session: Session) -> list[int]:
        if self.ids:
            return list(self.ids)

        # Every fragment below is a literal; values are bound, never interpolated.
        clauses: list[str] = []
        params: dict[str, int] = {}

        if self.blank_names:
            clauses.append("(name = '' OR name IS NULL)")
        if self.fabricated_dates:
            clauses.append(
                "(join_date IN (SELECT join_date FROM members WHERE join_date IS NOT NULL"
                " GROUP BY join_date HAVING COUNT(*) >= :threshold))"
            )
            params["threshold"] = FABRICATED_DATE_THRESHOLD
        if not clauses:
            return []

        # two values are bound parameters. Ruff cannot see that from here.
        sql = "SELECT id FROM members WHERE " + " OR ".join(clauses) + " ORDER BY id"  # noqa: S608
        if self.limit:
            sql += " LIMIT :limit"
            params["limit"] = self.limit
        return [int(row[0]) for row in session.execute(text(sql), params)]


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
    verify: CliSubCommand[Verify]
    refresh_members: CliSubCommand[RefreshMembers]
    check: CliSubCommand[Check]

    def cli_cmd(self) -> None:
        configure_logging(verbose=self.verbose)
        warning = env_file_permission_warning()
        if warning:
            logger.warning(warning)
        CliApp.run_subcommand(self)


def main() -> None:
    CliApp.run(Cli)


if __name__ == "__main__":
    main()
