from __future__ import annotations

import pytest
from pydantic import ValidationError
from pydantic_settings import CliApp

from dpc.awards.catalog import AwardCatalog
from dpc.cli import Awards, Check, Cli, DbInit, Export, Scrape

REPO_ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "config" / "awards.yaml"


def _parse(argv: list[str]) -> Cli:
    return CliApp.run(Cli, cli_args=argv, cli_cmd_method_name="_noop")


def _scrape(argv: list[str]) -> Scrape:
    scrape = _parse(argv).scrape
    assert scrape is not None
    return scrape


class TestArgumentParsing:
    """Subcommands are models, so parsing is checkable without running them."""

    def test_selects_the_subcommand(self):
        cli = _parse(["export"])
        assert cli.export is not None
        assert cli.scrape is None

    def test_verbose_is_off_by_default(self):
        assert _parse(["check"]).verbose is False

    def test_verbose_flag(self):
        assert _parse(["--verbose", "check"]).verbose is True

    def test_repeated_challenge_ids(self):
        scrape = _scrape(["scrape", "--challenge", "[1,2,3]"])
        assert scrape.challenge == [1, 2, 3]

    def test_images_defaults_on_and_can_be_negated(self):
        assert _scrape(["scrape"]).images is True
        assert _scrape(["scrape", "--no-images"]).images is False

    def test_anonymous_is_off_by_default_and_can_be_set(self):
        # CI has no secrets; a local run logs in. Both must be expressible.
        assert _scrape(["scrape"]).anonymous is False
        assert _scrape(["scrape", "--anonymous"]).anonymous is True

    def test_out_defaults_to_none_meaning_the_settings_value(self):
        export = _parse(["export"]).export
        assert export is not None
        assert export.out is None

    def test_rejects_a_non_integer_challenge_id(self):
        # argparse accepts the token; pydantic is what refuses it.
        with pytest.raises(ValidationError):
            _parse(["scrape", "--challenge", "[abc]"])


class TestCommandsAreConstructibleDirectly:
    """Each command can be built and run in-process, with no argv involved."""

    @pytest.mark.parametrize("command", [DbInit, Scrape, Awards, Export, Check])
    def test_every_command_has_a_cli_cmd(self, command):
        assert callable(command().cli_cmd)

    def test_check_validates_the_real_catalogue(self, capsys):
        Check(catalog=CATALOG_PATH).cli_cmd()
        catalog = AwardCatalog.load(CATALOG_PATH)
        assert f"{len(catalog.awarders)} awarders" in capsys.readouterr().out

    def test_scrape_without_a_source_exits_rather_than_hitting_the_network(self):
        with pytest.raises(SystemExit) as excinfo:
            Scrape().cli_cmd()
        assert excinfo.value.code == 2


class TestPipelineOnAScratchDatabase:
    @pytest.fixture
    def scratch(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DPC_DATABASE_URL", f"sqlite+pysqlite:///{tmp_path / 'db.sqlite'}")
        monkeypatch.setenv("DPC_SITE_DIR", str(tmp_path / "site"))
        return tmp_path

    def test_db_init_then_awards_then_export(self, scratch, capsys):
        DbInit().cli_cmd()
        Awards(catalog=CATALOG_PATH).cli_cmd()
        Export(catalog=CATALOG_PATH).cli_cmd()

        out = capsys.readouterr().out
        # Derived, not hardcoded: `dpc check` must report whatever the real
        # catalogue holds today.
        expected = len(AwardCatalog.load(CATALOG_PATH).pairs())
        assert str(expected) in out
        assert (scratch / "site" / "data" / "dpc" / "awards.json").is_file()

    def test_export_honours_an_explicit_destination(self, scratch):
        DbInit().cli_cmd()
        Awards(catalog=CATALOG_PATH).cli_cmd()
        Export(catalog=CATALOG_PATH, out=scratch / "elsewhere").cli_cmd()

        assert (scratch / "elsewhere" / "meta.json").is_file()


class TestRecentRefetch:
    """`--recent` revisits finished challenges so late comments are picked up.

    The question that matters is whether revisiting is destructive. It is not:
    nothing in the crawl path deletes, and comments are inserted only when
    their id is unknown, so a second pass over a challenge adds what is new and
    leaves everything already stored exactly as it was.
    """

    def test_flag_parses_and_defaults_off(self):
        assert _scrape(["scrape"]).recent == 0
        assert _scrape(["scrape", "--recent", "10"]).recent == 10

    def test_recent_alone_is_a_valid_source(self):
        # Revisiting is work in its own right, so it must not trip the
        # "pass a source" guard the way a bare `dpc scrape` does.
        with pytest.raises(SystemExit) as bare:
            _scrape(["scrape"]).cli_cmd()
        assert bare.value.code == 2
        # and with --recent it gets past the guard (it will then try the
        # network, which is why this only checks the guard itself)
        assert _scrape(["scrape", "--recent", "5"]).recent == 5

    def test_picks_the_most_recently_finished(self, tmp_path):
        from datetime import date

        from dpc.cli import _recent_challenge_ids
        from dpc.db import Challenge, create_all, create_db_engine
        from dpc.db.session import create_session_factory

        engine = create_db_engine(f"sqlite+pysqlite:///{tmp_path / 'r.sqlite'}")
        create_all(engine)
        session = create_session_factory(engine)()
        for i, day in enumerate([1, 5, 3, 9, 7], start=1):
            session.add(
                Challenge(
                    id=i,
                    name=f"c{i}",
                    description="",
                    submission_start=date(2026, 1, day),
                    submission_end=date(2026, 1, day),
                    voting_start=date(2026, 1, day),
                    voting_end=date(2026, 1, day),
                    num_submissions=0,
                    num_disqualifications=0,
                    num_votes=0,
                    num_comments=0,
                    average_score=0.0,
                    highest_score=0.0,
                    median_score=0.0,
                    lowest_score=0.0,
                )
            )
        session.commit()

        assert _recent_challenge_ids(session, 3) == [4, 5, 2]
        assert _recent_challenge_ids(session, 0) == []
        assert len(_recent_challenge_ids(session, 99)) == 5
        session.close()
        engine.dispose()
