"""An explicit `default: null` is distinct from no default.

`VariableDefinition.default` collapses both to `None`, so a flow cannot tell a
default that was declared null from one that was never declared. Downstream (in
Wyrdbound) that distinction is load-bearing: an output or variable that declares
`default` starts with that value — which may be null — while one that declares
nothing is absent until the flow sets it, and reading it is an error. See
wyrdbound 02-spec-findings.md F50.
"""

from pathlib import Path

import pytest
import yaml

from grimoire.loader import SystemLoader

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"


def _write_system(root: Path, body: str) -> Path:
    (root / "flows").mkdir(parents=True)
    (root / "system.yaml").write_text(
        yaml.safe_dump({"id": "t", "kind": "system", "name": "T"})
    )
    (root / "flows" / "f.yaml").write_text(
        "id: f\nkind: flow\nname: F\n"
        f"{body}"
        "steps:\n  - id: done\n    type: completion\n"
    )
    return root


def _vars(section: str, entry: str) -> str:
    return f"{section}:\n{entry}"


# --- inputs -----------------------------------------------------------------


def test_an_input_without_a_default_has_none_declared(tmp_path: Path) -> None:
    root = _write_system(tmp_path, _vars("inputs", "  - {id: a, type: str}\n"))
    parsed = SystemLoader().load(root).flows["f"].inputs[0]
    assert parsed.default is None
    assert parsed.has_default is False


def test_an_input_with_an_explicit_null_default_declares_one(tmp_path: Path) -> None:
    root = _write_system(
        tmp_path, _vars("inputs", "  - {id: a, type: str, default: null}\n")
    )
    parsed = SystemLoader().load(root).flows["f"].inputs[0]
    assert parsed.default is None
    assert parsed.has_default is True


def test_an_input_with_a_value_default_declares_one(tmp_path: Path) -> None:
    root = _write_system(
        tmp_path, _vars("inputs", "  - {id: a, type: str, default: hi}\n")
    )
    parsed = SystemLoader().load(root).flows["f"].inputs[0]
    assert parsed.default == "hi"
    assert parsed.has_default is True


# --- outputs ----------------------------------------------------------------


def test_an_output_without_a_default_has_none_declared(tmp_path: Path) -> None:
    root = _write_system(tmp_path, _vars("outputs", "  - {id: a, type: str}\n"))
    parsed = SystemLoader().load(root).flows["f"].outputs[0]
    assert parsed.default is None
    assert parsed.has_default is False


def test_an_output_with_an_explicit_null_default_declares_one(tmp_path: Path) -> None:
    root = _write_system(
        tmp_path, _vars("outputs", "  - {id: a, type: str, default: null}\n")
    )
    parsed = SystemLoader().load(root).flows["f"].outputs[0]
    assert parsed.default is None
    assert parsed.has_default is True


@pytest.mark.parametrize("value", ["0", "[]", "''"])
def test_an_output_with_a_falsy_default_declares_one(
    tmp_path: Path, value: str
) -> None:
    root = _write_system(
        tmp_path, _vars("outputs", f"  - {{id: a, type: list, default: {value}}}\n")
    )
    parsed = SystemLoader().load(root).flows["f"].outputs[0]
    assert parsed.has_default is True


# --- variables --------------------------------------------------------------


def test_a_variable_without_a_default_has_none_declared(tmp_path: Path) -> None:
    root = _write_system(tmp_path, _vars("variables", "  - {id: a, type: int}\n"))
    parsed = SystemLoader().load(root).flows["f"].variables[0]
    assert parsed.default is None
    assert parsed.has_default is False


def test_a_variable_with_an_explicit_null_default_declares_one(tmp_path: Path) -> None:
    root = _write_system(
        tmp_path, _vars("variables", "  - {id: a, type: int, default: null}\n")
    )
    parsed = SystemLoader().load(root).flows["f"].variables[0]
    assert parsed.default is None
    assert parsed.has_default is True


def test_a_variable_with_a_value_default_declares_one(tmp_path: Path) -> None:
    root = _write_system(
        tmp_path, _vars("variables", "  - {id: a, type: int, default: 0}\n")
    )
    parsed = SystemLoader().load(root).flows["f"].variables[0]
    assert parsed.default == 0
    assert parsed.has_default is True


@pytest.mark.parametrize("system", ["knave-1e", "wyrdbound-quickstart-1e"])
def test_reference_systems_parse_the_flag(system: str) -> None:
    loaded = SystemLoader().load(SYSTEMS_DIR / system)
    for flow in loaded.flows.values():
        for section in (flow.inputs, flow.outputs, flow.variables):
            for var in section or ():
                assert getattr(var, "has_default", False) is True or var.default is None
