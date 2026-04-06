from pathlib import Path

from maestro.archetypes import load_archetype_pack


def test_load_archetype_pack_reads_yaml() -> None:
    root = Path(__file__).resolve().parents[1] / "archetypes"
    pack = load_archetype_pack("saas_app", root)

    assert pack.name == "saas_app"
    assert "auth" in pack.architecture_defaults["domains"]
