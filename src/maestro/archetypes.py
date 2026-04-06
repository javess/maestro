from __future__ import annotations

from pathlib import Path

import yaml

from maestro.schemas.archetype import ArchetypePack


def load_archetype_pack(name: str, root: Path) -> ArchetypePack:
    path = root / f"{name}.yaml"
    data = yaml.safe_load(path.read_text()) or {}
    return ArchetypePack.model_validate(data)
