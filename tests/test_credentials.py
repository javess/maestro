import sys
from types import ModuleType

import pytest
from typer.testing import CliRunner

from maestro.cli.main import app
from maestro.credentials import (
    DEFAULT_CREDENTIAL_SERVICE,
    credential_status,
    resolve_provider_secret,
    store_provider_secret,
)


class _FakeKeyring(ModuleType):
    def __init__(self) -> None:
        super().__init__("keyring")
        self.values: dict[tuple[str, str], str] = {}

    def get_password(self, service_name: str, credential_name: str) -> str | None:
        return self.values.get((service_name, credential_name))

    def set_password(self, service_name: str, credential_name: str, secret: str) -> None:
        self.values[(service_name, credential_name)] = secret

    def delete_password(self, service_name: str, credential_name: str) -> None:
        self.values.pop((service_name, credential_name), None)


@pytest.fixture
def fake_keyring(monkeypatch: pytest.MonkeyPatch) -> _FakeKeyring:
    module = _FakeKeyring()
    monkeypatch.setitem(sys.modules, "keyring", module)
    return module


def test_store_and_resolve_provider_secret_via_keyring(
    monkeypatch: pytest.MonkeyPatch, fake_keyring: _FakeKeyring
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    store_provider_secret(provider="openai", secret="secure-value")

    assert (
        fake_keyring.get_password(DEFAULT_CREDENTIAL_SERVICE, "OPENAI_API_KEY") == "secure-value"
    )
    assert (
        resolve_provider_secret(api_key_env="OPENAI_API_KEY", provider="openai") == "secure-value"
    )


def test_credential_status_prefers_env_over_keyring(
    monkeypatch: pytest.MonkeyPatch, fake_keyring: _FakeKeyring
) -> None:
    fake_keyring.set_password(DEFAULT_CREDENTIAL_SERVICE, "OPENAI_API_KEY", "stored")
    monkeypatch.setenv("OPENAI_API_KEY", "from-env")

    status = credential_status(provider="openai")

    assert status["env_present"] is True
    assert status["keyring_present"] is True
    assert status["resolved_source"] == "env"


def test_creds_cli_set_status_and_delete(
    monkeypatch: pytest.MonkeyPatch, fake_keyring: _FakeKeyring
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    runner = CliRunner()

    set_result = runner.invoke(app, ["creds", "set", "openai", "--value", "secret-value"])
    assert set_result.exit_code == 0

    status_result = runner.invoke(app, ["creds", "status", "openai"])
    assert status_result.exit_code == 0
    assert "keyring_present" in status_result.stdout

    delete_result = runner.invoke(app, ["creds", "delete", "openai"])
    assert delete_result.exit_code == 0
    assert fake_keyring.get_password(DEFAULT_CREDENTIAL_SERVICE, "OPENAI_API_KEY") is None
