"""The quickstart stores `spells` as a list, not JSON text (wyrdbound F52).

`character_creation`'s `select_spells` step built the list, then applied
`| tojson`, which returns text. The `character` model declares
`spells: {type: list, of: str}`, so the write was rejected
("Field 'spells' must be a list, got Markup"). The list expression without the
filter is already the right value.

This test is static: it checks the action's template, which is what the
grimoire suite can see without an engine.
"""

from pathlib import Path

import yaml

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"
FLOW = SYSTEMS_DIR / "wyrdbound-quickstart-1e" / "flows" / "character_creation.yaml"

SPELLS_PATH = "outputs.character.spells"


def _spells_value() -> str:
    flow = yaml.safe_load(FLOW.read_text())
    for step in flow["steps"]:
        for action in step.get("actions") or []:
            value = (action.get("set_value") or {}).get("path")
            if value == SPELLS_PATH:
                return action["set_value"]["value"]
    raise AssertionError(f"no set_value for {SPELLS_PATH!r} in character_creation")


def test_spells_is_not_serialised_to_json() -> None:
    value = _spells_value()

    assert "tojson" not in value, (
        "`| tojson` makes the value a string; the model wants a list (wyrdbound F52)"
    )


def test_spells_value_is_a_list_expression() -> None:
    value = _spells_value()

    assert "| list" in value
    assert value.startswith("{{") and value.endswith("}}")
