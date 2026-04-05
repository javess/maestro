from __future__ import annotations

from pathlib import Path

import yaml

from maestro.schemas.contracts import PolicyPack


def load_policy(name: str, root: Path) -> PolicyPack:
    path = root / f"{name}.yaml"
    data = yaml.safe_load(path.read_text()) or {}
    return PolicyPack.model_validate(data)
