"""An output's `validate` flag is parsed (`spec/flow_spec.md`, "Inputs,
Outputs, and Variables"): an engine cannot validate an output the loader has
forgotten was marked."""

from pathlib import Path

import yaml

from grimoire.loader import SystemLoader


def _load_outputs(root: Path, outputs_yaml: str) -> list:
    (root / "flows").mkdir(parents=True)
    (root / "system.yaml").write_text(
        yaml.safe_dump({"id": "t", "kind": "system", "name": "T"})
    )
    (root / "flows" / "f.yaml").write_text(
        "id: f\nkind: flow\nname: F\n"
        f"outputs:\n{outputs_yaml}"
        "steps:\n  - id: done\n    type: completion\n"
    )
    return SystemLoader().load(root).flows["f"].outputs


def test_validate_is_parsed(tmp_path: Path) -> None:
    (output,) = _load_outputs(tmp_path, "  - {id: c, type: str, validate: true}\n")
    assert output.validate is True


def test_validate_defaults_to_false(tmp_path: Path) -> None:
    (output,) = _load_outputs(tmp_path, "  - {id: c, type: str}\n")
    assert output.validate is False
