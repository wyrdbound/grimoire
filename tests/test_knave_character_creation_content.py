"""Knave's character creation content runs as written.

Pins the five content fixes found by running the flow (Wyrdbound findings
F58, F59, F63, F64 and F65):

- name and gender are chosen before the weapon step (F58);
- each gender choice writes ``{{ result.id }}`` and the gender table's entries
  are the model enum's lowercase spellings (F59);
- the weapon step writes ``{{ result.knave }}``, not the sub-flow's whole
  outputs (F63);
- ``armor.bonus`` has a default, so an unarmoured Knave is valid (F64);
- ``min_probability`` is a number, not the string YAML 1.1 reads ``1e-4``
  as (F65).
"""

from pathlib import Path

import yaml

from grimoire.loader import SystemLoader

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"
KNAVE_DIR = SYSTEMS_DIR / "knave-1e"
CHAR_FLOW = KNAVE_DIR / "flows" / "character_creation.yaml"
NAME_FLOW = KNAVE_DIR / "flows" / "character_creation" / "choose_name_and_gender.yaml"
GENDER_TABLE = KNAVE_DIR / "tables" / "misc" / "gender.yaml"
CHARACTER_MODEL = KNAVE_DIR / "models" / "character.yaml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def _step(flow: dict, step_id: str) -> dict:
    return next(s for s in flow["steps"] if s["id"] == step_id)


def _linear_order(flow: dict) -> list[str]:
    """Walk the flow's ``next_step`` chain from its first step."""
    step = flow["steps"][0]
    order: list[str] = []
    while step["id"] not in order:
        order.append(step["id"])
        next_step = step.get("next_step")
        if next_step is None:
            break
        step = _step(flow, next_step)
    return order


def test_name_and_gender_are_chosen_before_gear() -> None:
    """F58: ``character.name`` exists before ``add_item_to_character`` logs it."""
    order = _linear_order(_load(CHAR_FLOW))
    expected = [
        "invoke_roll_abilities",
        "invoke_roll_hit_points",
        "invoke_choose_name_and_gender",
        "invoke_choose_starting_weapon",
        "invoke_determine_traits",
        "generate_character_description",
    ]

    indices = [order.index(step_id) for step_id in expected]

    assert indices == sorted(indices)


def test_gender_choices_write_the_choice_id() -> None:
    """F59: ``result.id`` is the enum's own lowercase spelling."""
    choice_step = _step(_load(NAME_FLOW), "choose_gender")

    for choice_id in ("female", "male", "non_binary"):
        choice = next(c for c in choice_step["choices"] if c["id"] == choice_id)
        values = [
            action["set_value"]["value"]
            for action in choice["actions"]
            if "set_value" in action
        ]
        assert values == ["{{ result.id }}"]


def test_gender_table_entries_match_the_model_enum() -> None:
    """F59: the rolled gender also passes the model's enum."""
    entries = _load(GENDER_TABLE)["entries"]

    assert list(entries.values()) == ["female", "male", "non-binary"]


def test_the_weapon_step_writes_the_sub_flows_knave() -> None:
    """F63: the whole sub-flow outputs must not be nested under ``knave``."""
    step = _step(_load(CHAR_FLOW), "invoke_choose_starting_weapon")
    values = [
        action["set_value"]["value"]
        for action in step["actions"]
        if "set_value" in action
    ]

    assert values == ["{{ result.knave }}"]


def test_armor_bonus_has_a_default() -> None:
    """F64: nothing in creation sets ``armor.bonus``, so it needs a default."""
    bonus = _load(CHARACTER_MODEL)["attributes"]["armor"]["bonus"]

    assert bonus == {"type": "int", "range": "0..10", "default": 1}


def test_min_probability_is_a_number() -> None:
    """F65: YAML 1.1 reads ``1e-4`` as a string."""
    step = _step(_load(NAME_FLOW), "randomly_generate_name")

    assert step["settings"]["min_probability"] == 0.0001
    assert isinstance(step["settings"]["min_probability"], float)


def test_the_system_loads_and_validates_with_the_fixes() -> None:
    system = SystemLoader().load(KNAVE_DIR)

    assert system.validate() == []
    assert "character_creation" in system.flows
