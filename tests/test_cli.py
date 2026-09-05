from __future__ import annotations

import pytest
from pydantic import ValidationError
from pydantic_settings import CliApp

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
        assert "18 awarders" in capsys.readouterr().out

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
        assert "38" in out  # the catalogue's 38 awards
        assert (scratch / "site" / "data" / "dpc" / "awards.json").is_file()

    def test_export_honours_an_explicit_destination(self, scratch):
        DbInit().cli_cmd()
        Awards(catalog=CATALOG_PATH).cli_cmd()
        Export(catalog=CATALOG_PATH, out=scratch / "elsewhere").cli_cmd()

        assert (scratch / "elsewhere" / "meta.json").is_file()
