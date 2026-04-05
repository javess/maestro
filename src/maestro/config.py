from __future__ import annotations

from pathlib import Path

import yaml

from maestro.schemas.contracts import MaestroConfig


def load_config(path: Path) -> MaestroConfig:
    data = yaml.safe_load(path.read_text()) or {}
    return MaestroConfig.model_validate(data)
