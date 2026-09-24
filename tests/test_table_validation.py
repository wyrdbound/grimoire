"""Table entries resolve against the system (spec/table_spec.md)."""

from pathlib import Path
from typing import Any

import pytest

from grimoire.loader import SystemLoader
from grimoire.models.system import System
from grimoire.models.table import TableDefinition

QUICKSTART = Path(__file__).parent.parent / "systems" / "wyrdbound-quickstart-1e"


@pytest.fixture(scope="module")
def system() -> System:
    return SystemLoader().load(QUICKSTART)


def _errors(system: System, entries: dict[Any, Any], entry_type: str) -> list[str]:
    table = TableDefinition(
        kind="table", name="T", id="t", entry_type=entry_type, entries=entries
    )
    return table.validate_with_system(system)


def test_validate_does_not_roll_dice() -> None:
    table = TableDefinition(kind="table", name="T", roll="1d6", entries={1: "a"})
    assert table.validate() == []


def test_string_reference_resolves(system: System) -> None:
    assert _errors(system, {1: "dagger"}, "weapon") == []


def test_unknown_string_reference_is_reported(system: System) -> None:
    errors = _errors(system, {1: "lightsaber"}, "weapon")
    assert errors == ["Entry '1': 'lightsaber' is not in any 'weapon' compendium"]


def test_null_entry_means_nothing(system: System) -> None:
    assert _errors(system, {"1-3": None, 4: "dagger"}, "weapon") == []


def test_reference_mapping_uses_its_own_type(system: System) -> None:
    assert (
        _errors(system, {1: {"id": "leather_armor", "type": "armor"}}, "weapon") == []
    )
    errors = _errors(system, {1: {"id": "dagger", "type": "armor"}}, "weapon")
    assert "'dagger' is not in any 'armor' compendium" in errors[0]


def test_random_and_generate_references_need_a_known_model(system: System) -> None:
    assert _errors(system, {1: {"type": "weapon"}, 2: {"generate": True}}, "item") == []
    errors = _errors(system, {1: {"type": "spaceship"}}, "item")
    assert errors == ["Entry '1' references unknown model 'spaceship'"]


def test_unknown_entry_type_is_reported(system: System) -> None:
    assert _errors(system, {1: "x"}, "spaceship") == [
        "entry_type 'spaceship' references unknown model"
    ]


def test_nested_tables_must_exist(system: System) -> None:
    assert _errors(system, {1: "gear"}, "table") == []
    assert _errors(system, {1: "nope"}, "table") == [
        "Entry '1' references unknown table 'nope'"
    ]


def test_system_validate_reports_table_errors(system: System) -> None:
    system.tables["gear"].entries[99] = "lightsaber"
    try:
        errors = [e for e in system.validate() if e.startswith("Table 'gear'")]
    finally:
        del system.tables["gear"].entries[99]
    assert errors == [
        "Table 'gear': Entry '99': 'lightsaber' is not in any 'item' compendium"
    ]
