from __future__ import annotations

import importlib
import logging
import os
from dataclasses import dataclass
from typing import Protocol, cast

logger = logging.getLogger(__name__)

DEFAULT_CREDENTIAL_SERVICE = "maestro"
PROVIDER_ENV_NAMES = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
}


class KeyringModule(Protocol):
    def get_password(self, service_name: str, credential_name: str) -> str | None: ...
    def set_password(self, service_name: str, credential_name: str, secret: str) -> None: ...
    def delete_password(self, service_name: str, credential_name: str) -> None: ...


@dataclass(frozen=True)
class CredentialTarget:
    provider: str
    env_name: str
    service_name: str
    credential_name: str


def resolve_credential_target(
    provider: str,
    *,
    env_name: str | None = None,
    service_name: str = DEFAULT_CREDENTIAL_SERVICE,
    credential_name: str | None = None,
) -> CredentialTarget:
    normalized_provider = provider.lower()
    resolved_env = env_name or PROVIDER_ENV_NAMES.get(normalized_provider)
    if resolved_env is None:
        raise ValueError(f"Unsupported provider for credential storage: {provider}")
    return CredentialTarget(
        provider=normalized_provider,
        env_name=resolved_env,
        service_name=service_name,
        credential_name=credential_name or resolved_env,
    )


def resolve_provider_secret(
    *,
    api_key_env: str,
    provider: str,
    service_name: str = DEFAULT_CREDENTIAL_SERVICE,
    credential_name: str | None = None,
) -> str | None:
    env_value = os.environ.get(api_key_env)
    if env_value:
        logger.debug("credential_resolved source=env provider=%s env=%s", provider, api_key_env)
        return env_value
    keyring = _load_keyring(optional=True)
    if keyring is None:
        return None
    target = resolve_credential_target(
        provider,
        env_name=api_key_env,
        service_name=service_name,
        credential_name=credential_name,
    )
    secret = keyring.get_password(target.service_name, target.credential_name)
    if secret:
        logger.info(
            "credential_resolved source=keyring provider=%s service=%s name=%s",
            provider,
            target.service_name,
            target.credential_name,
        )
    return secret


def store_provider_secret(
    *,
    provider: str,
    secret: str,
    env_name: str | None = None,
    service_name: str = DEFAULT_CREDENTIAL_SERVICE,
    credential_name: str | None = None,
) -> CredentialTarget:
    keyring = cast(KeyringModule, _load_keyring(optional=False))
    target = resolve_credential_target(
        provider,
        env_name=env_name,
        service_name=service_name,
        credential_name=credential_name,
    )
    keyring.set_password(target.service_name, target.credential_name, secret)
    logger.info(
        "credential_stored provider=%s service=%s name=%s",
        target.provider,
        target.service_name,
        target.credential_name,
    )
    return target


def delete_provider_secret(
    *,
    provider: str,
    env_name: str | None = None,
    service_name: str = DEFAULT_CREDENTIAL_SERVICE,
    credential_name: str | None = None,
) -> CredentialTarget:
    keyring = cast(KeyringModule, _load_keyring(optional=False))
    target = resolve_credential_target(
        provider,
        env_name=env_name,
        service_name=service_name,
        credential_name=credential_name,
    )
    try:
        keyring.delete_password(target.service_name, target.credential_name)
    except Exception as error:  # noqa: BLE001
        logger.warning(
            "credential_delete_failed provider=%s service=%s name=%s error=%s",
            target.provider,
            target.service_name,
            target.credential_name,
            error,
        )
    return target


def credential_status(
    *,
    provider: str,
    env_name: str | None = None,
    service_name: str = DEFAULT_CREDENTIAL_SERVICE,
    credential_name: str | None = None,
) -> dict[str, str | bool]:
    target = resolve_credential_target(
        provider,
        env_name=env_name,
        service_name=service_name,
        credential_name=credential_name,
    )
    env_present = bool(os.environ.get(target.env_name))
    keyring = _load_keyring(optional=True)
    keyring_present = False
    if keyring is not None:
        keyring_present = bool(keyring.get_password(target.service_name, target.credential_name))
    return {
        "provider": target.provider,
        "env_name": target.env_name,
        "service_name": target.service_name,
        "credential_name": target.credential_name,
        "env_present": env_present,
        "keyring_present": keyring_present,
        "resolved_source": "env" if env_present else ("keyring" if keyring_present else "missing"),
    }


def _load_keyring(*, optional: bool) -> KeyringModule | None:
    try:
        return cast(KeyringModule, importlib.import_module("keyring"))
    except ModuleNotFoundError as error:
        if optional:
            logger.debug("keyring_not_installed_optional")
            return None
        raise RuntimeError(
            "The `keyring` package is not installed; run `uv sync --all-extras` "
            "to enable secure credential storage"
        ) from error
