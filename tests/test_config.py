from __future__ import annotations

import json
import logging

import pytest
from pydantic import ValidationError

from dpc.config import Credentials, Settings

SECRET = "hunter2-do-not-leak"  # noqa: S105 - a deliberate canary, not a real secret


@pytest.fixture
def credentials(monkeypatch):
    monkeypatch.setenv("DPC_USERNAME", "NiallOTuama")
    monkeypatch.setenv("DPC_PASSWORD", SECRET)
    return Credentials(_env_file=None)


class TestSettings:
    def test_loads_without_any_credentials(self, monkeypatch):
        # Export and site builds must not require a login, so Settings has to be
        # constructible with an empty environment.
        monkeypatch.delenv("DPC_USERNAME", raising=False)
        monkeypatch.delenv("DPC_PASSWORD", raising=False)
        settings = Settings(_env_file=None)
        assert settings.database_url.startswith("sqlite+pysqlite:///")

    def test_export_dir_hangs_off_site_dir(self, tmp_path):
        settings = Settings(_env_file=None, site_dir=tmp_path)
        assert settings.export_dir == tmp_path / "data" / "dpc"

    def test_env_overrides_defaults(self, monkeypatch):
        monkeypatch.setenv("DPC_REQUEST_DELAY", "2.5")
        assert Settings(_env_file=None).request_delay == 2.5


class TestCredentials:
    def test_requires_a_username_and_password(self, monkeypatch):
        monkeypatch.delenv("DPC_USERNAME", raising=False)
        monkeypatch.delenv("DPC_PASSWORD", raising=False)
        with pytest.raises(ValidationError):
            Credentials(_env_file=None)

    def test_login_form_carries_the_real_password(self, credentials):
        form = credentials.as_login_form()
        assert form["PASSWORD"] == SECRET
        assert form["USERNAME"] == "NiallOTuama"

    def test_login_form_supplies_the_non_secret_constants(self, credentials):
        # These sat next to the real password in login_details.json; they are
        # form fields, not secrets.
        form = credentials.as_login_form()
        assert form["SAVE_PASSWORD"] == "1"  # noqa: S105 - a form flag, not a password
        assert form["REDIRECT"] == "/index.php"


class TestThePasswordNeverLeaks:
    """`no pwords at all are logged` -- enforced, not just intended."""

    def test_not_in_repr(self, credentials):
        assert SECRET not in repr(credentials)

    def test_not_in_str(self, credentials):
        assert SECRET not in str(credentials)

    def test_not_in_the_password_fields_own_repr(self, credentials):
        assert SECRET not in repr(credentials.password)

    def test_not_in_a_model_dump(self, credentials):
        assert SECRET not in str(credentials.model_dump())

    def test_not_in_a_json_dump(self, credentials):
        assert SECRET not in credentials.model_dump_json()

    def test_not_in_a_formatted_log_record(self, credentials, caplog):
        with caplog.at_level(logging.INFO):
            logging.getLogger("test").info("credentials are %s", credentials)
        assert SECRET not in caplog.text

    def test_reaching_the_value_takes_an_explicit_call(self, credentials):
        # The only way out is get_secret_value(), which greps trivially.
        assert credentials.password.get_secret_value() == SECRET

    def test_not_in_a_validation_error_for_a_sibling_field(self, monkeypatch):
        monkeypatch.setenv("DPC_USERNAME", "someone")
        monkeypatch.setenv("DPC_PASSWORD", SECRET)
        monkeypatch.setenv("DPC_REQUEST_TIMEOUT", "not-a-number")
        with pytest.raises(ValidationError) as excinfo:
            Settings(_env_file=None)
        assert SECRET not in str(excinfo.value)
        assert SECRET not in json.dumps(excinfo.value.errors(), default=str)
