from __future__ import annotations

import logging

from rich.logging import RichHandler


def resolve_log_level(verbose: int = 0, quiet: bool = False, log_level: str | None = None) -> int:
    if log_level:
        return getattr(logging, log_level.upper(), logging.INFO)
    if quiet:
        return logging.ERROR
    if verbose >= 2:
        return logging.DEBUG
    if verbose == 1:
        return logging.INFO
    return logging.WARNING


def configure_logging(
    *,
    verbose: int = 0,
    quiet: bool = False,
    log_level: str | None = None,
) -> int:
    level = resolve_log_level(verbose=verbose, quiet=quiet, log_level=log_level)
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, show_time=False, show_path=False)],
        force=True,
    )
    return level
