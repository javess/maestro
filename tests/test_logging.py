import logging

from maestro.logging import (
    configure_logging,
    log_provider_request,
    log_provider_response,
    resolve_log_level,
)


def test_resolve_log_level_defaults_to_warning() -> None:
    assert resolve_log_level() == logging.WARNING


def test_resolve_log_level_uses_verbose_flags() -> None:
    assert resolve_log_level(verbose=1) == logging.INFO
    assert resolve_log_level(verbose=2) == logging.DEBUG


def test_resolve_log_level_honors_explicit_override() -> None:
    assert resolve_log_level(verbose=2, log_level="error") == logging.ERROR


def test_configure_logging_returns_configured_level() -> None:
    assert configure_logging(log_level="info") == logging.INFO


def test_log_provider_request_emits_prompt_and_metadata(caplog) -> None:
    logger = logging.getLogger("maestro.test.logging")
    with caplog.at_level(logging.DEBUG):
        log_provider_request(
            logger,
            provider="openai",
            action="generate_structured",
            model="gpt-5",
            prompt="INPUT={'ticket':'TICKET-1'}",
            metadata={"role": "coder"},
            schema_name="CodeResult",
        )
    assert "provider_request provider=openai" in caplog.text
    assert "INPUT={'ticket':'TICKET-1'}" in caplog.text
    assert "'role': 'coder'" in caplog.text


def test_log_provider_response_emits_payload(caplog) -> None:
    logger = logging.getLogger("maestro.test.logging")
    with caplog.at_level(logging.DEBUG):
        log_provider_response(
            logger,
            provider="fake",
            action="generate_structured",
            model="fake-model",
            payload='{"ok": true}',
            schema_name="Backlog",
        )
    assert "provider_response provider=fake" in caplog.text
    assert '{"ok": true}' in caplog.text
