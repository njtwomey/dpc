from __future__ import annotations

import json
import logging

import pytest
from pydantic import ValidationError

from dpc.config import (
    Credentials,
    Settings,
    env_file_permission_warning,
    restrict_env_file,
)

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


class TestEnvFilePermissions:
    """`.env` holds a plaintext password, so it must be owner-readable only."""

    @pytest.fixture
    def env_file(self, tmp_path):
        path = tmp_path / ".env"
        path.write_text("DPC_PASSWORD=whatever\n", encoding="utf-8")
        return path

    def test_no_warning_when_locked_down(self, env_file):
        env_file.chmod(0o600)
        assert env_file_permission_warning(env_file) is None

    @pytest.mark.parametrize("mode", [0o644, 0o640, 0o604, 0o666, 0o660])
    def test_warns_when_anyone_else_can_read_it(self, env_file, mode):
        env_file.chmod(mode)
        warning = env_file_permission_warning(env_file)
        assert warning is not None
        assert "chmod 600" in warning

    def test_the_warning_never_quotes_the_contents(self, env_file):
        env_file.write_text(f"DPC_PASSWORD={SECRET}\n", encoding="utf-8")
        env_file.chmod(0o644)
        warning = env_file_permission_warning(env_file)
        assert warning is not None
        assert SECRET not in warning

    def test_missing_file_is_not_a_warning(self, tmp_path):
        assert env_file_permission_warning(tmp_path / "absent") is None

    def test_restrict_tightens_a_loose_file(self, env_file):
        env_file.chmod(0o644)
        assert restrict_env_file(env_file) is True
        assert env_file.stat().st_mode & 0o777 == 0o600
        assert env_file_permission_warning(env_file) is None

    def test_restrict_is_a_no_op_when_already_tight(self, env_file):
        env_file.chmod(0o600)
        assert restrict_env_file(env_file) is False

    def test_the_real_env_file_is_locked_down(self):
        # Guards the actual working copy, not just the logic.
        warning = env_file_permission_warning()
        assert warning is None, warning
