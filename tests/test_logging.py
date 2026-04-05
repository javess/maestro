import logging

from maestro.logging import configure_logging, resolve_log_level


def test_resolve_log_level_defaults_to_warning() -> None:
    assert resolve_log_level() == logging.WARNING


def test_resolve_log_level_uses_verbose_flags() -> None:
    assert resolve_log_level(verbose=1) == logging.INFO
    assert resolve_log_level(verbose=2) == logging.DEBUG


def test_resolve_log_level_honors_explicit_override() -> None:
    assert resolve_log_level(verbose=2, log_level="error") == logging.ERROR


def test_configure_logging_returns_configured_level() -> None:
    assert configure_logging(log_level="info") == logging.INFO
