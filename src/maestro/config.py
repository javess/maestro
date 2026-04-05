from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml

from maestro.schemas.contracts import MaestroConfig

logger = logging.getLogger(__name__)


def load_env_file(path: Path) -> None:
    if not path.exists():
        logger.debug("env_file_missing path=%s", path)
        return
    logger.info("env_file_load path=%s", path)
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
            logger.debug("env_var_loaded key=%s source=%s", key, path)


def load_config(path: Path) -> MaestroConfig:
    load_env_file(path.parent / ".env")
    data = yaml.safe_load(path.read_text()) or {}
    config = MaestroConfig.model_validate(data)
    logger.info(
        "config_loaded path=%s policy=%s providers=%s",
        path,
        config.policy,
        ",".join(sorted(config.providers.keys())),
    )
    return config
