"""Flow inputs use `optional`, the same presence flag as model attributes."""

from pathlib import Path

import pytest
import yaml

from grimoire.loader import SystemLoader, SystemLoadError

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"


def _write_system(root: Path, input_yaml: str) -> Path:
    (root / "flows").mkdir(parents=True)
    (root / "system.yaml").write_text(
        yaml.safe_dump({"id": "t", "kind": "system", "name": "T"})
    )
    (root / "flows" / "f.yaml").write_text(
        "id: f\nkind: flow\nname: F\n"
        f"inputs:\n{input_yaml}"
        "steps:\n  - id: done\n    type: completion\n"
    )
    return root


def test_inputs_are_required_by_default(tmp_path: Path) -> None:
    system = SystemLoader().load(_write_system(tmp_path, "  - {id: a, type: str}\n"))
    assert system.flows["f"].inputs[0].optional is False


def test_optional_input_is_parsed(tmp_path: Path) -> None:
    root = _write_system(tmp_path, "  - {id: a, type: str, optional: true}\n")
    assert SystemLoader().load(root).flows["f"].inputs[0].optional is True


def test_required_field_is_rejected(tmp_path: Path) -> None:
    root = _write_system(tmp_path, "  - {id: a, type: str, required: true}\n")
    with pytest.raises(SystemLoadError, match="`required` is not a flow variable"):
        SystemLoader().load(root)


@pytest.mark.parametrize("system", ["knave-1e", "wyrdbound-quickstart-1e"])
def test_reference_systems_do_not_use_required(system: str) -> None:
    for path in (SYSTEMS_DIR / system / "flows").rglob("*.yaml"):
        data = yaml.safe_load(path.read_text())
        for section in ("inputs", "outputs", "variables"):
            for var in data.get(section) or []:
                assert "required" not in var, f"{path}: {var.get('id')}"
