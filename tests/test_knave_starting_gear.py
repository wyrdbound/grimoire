"""`roll_starting_gear` is complete and ready to be re-enabled.

`character_creation` skips starting gear (the step is commented out), but the
sub-flow itself is implemented: it rolls armour, helmets/shields,
dungeoneering gear (twice) and two general-gear tables, adding each roll
through the inventory flows. This is the preparation for re-enabling it — the
content is complete and loads; the caller's step stays commented until a
decision is made to switch it on.

The shape rules this pins:

- a single-entry table is read as `result.entry`;
- a `multiple_entries` table is read as `result.entries`;
- `table_sequence` (dungeoneering, rolled twice) appends `result.entry` per
  roll, and its step-level actions may not read `result`.
"""

from pathlib import Path

import pytest
import yaml

from grimoire.loader import SystemLoader

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"
KNAVE_DIR = SYSTEMS_DIR / "knave-1e"
GEAR_FLOW = KNAVE_DIR / "flows" / "character_creation" / "roll_starting_gear.yaml"
CHAR_FLOW = KNAVE_DIR / "flows" / "character_creation.yaml"


@pytest.fixture(scope="module")
def gear() -> dict:
    return yaml.safe_load(GEAR_FLOW.read_text())


def _step(flow: dict, step_id: str) -> dict:
    return next(s for s in flow["steps"] if s["id"] == step_id)


def test_starting_gear_flow_is_complete(gear: dict) -> None:
    """It reaches a completion step rather than trailing off."""
    types = [s["type"] for s in gear["steps"]]
    assert "completion" in types


def test_single_entry_tables_use_result_entry(gear: dict) -> None:
    for step_id in ("roll_armor", "roll_general_1", "roll_general_2"):
        for table in _step(gear, step_id)["tables"]:
            for action in table["actions"]:
                assert "result.entry" in action["set_value"]["value"]


def test_multiple_entries_table_uses_result_entries(gear: dict) -> None:
    table = _step(gear, "roll_helmets_and_shields")["tables"][0]
    value = table["actions"][0]["set_value"]["value"]

    assert "result.entries" in value
    assert "result.entry." not in value


def test_dungeoneering_gear_is_a_sequence_of_two(gear: dict) -> None:
    step = _step(gear, "roll_dungeoneering")

    assert step["type"] == "table_sequence"
    assert step["sequence"]["table"] == "dungeoneering_gear"
    assert step["sequence"]["count"] == 2


def test_the_system_loads_and_validates_with_the_gear_flow() -> None:
    system = SystemLoader().load(KNAVE_DIR)

    assert system.validate() == []
    assert "roll_starting_gear" in system.flows


def test_the_reenable_snippet_names_the_right_input_and_output() -> None:
    """The commented caller step must use the sub-flow's declared input id and
    read its output correctly, so uncommenting it works."""
    body = CHAR_FLOW.read_text()
    snippet = body[body.index("# - id: invoke_roll_starting_gear") :]

    assert 'knave: "{{ outputs.knave }}"' in snippet  # the sub-flow's input id
    assert 'value: "{{ result.knave }}"' in snippet


def test_helmet_and_shield_table_entry_is_read_as_a_collection() -> None:
    """A helmet/shield result is added as a list, never as a lone entry."""
    table = yaml.safe_load(
        (KNAVE_DIR / "tables" / "gear" / "helmets-and-shields.yaml").read_text()
    )
    assert table["multiple_entries"] is True
