"""`multiple_entries` tables and the load-time result-shape check."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from grimoire.loader import SystemLoader
from grimoire.models.result_shape import candidate_tables, result_fields
from grimoire.models.system import System
from grimoire.models.table import TableDefinition

KNAVE = Path(__file__).parent.parent / "systems" / "knave-1e"


def _system(tmp_path: Path, tables: dict[str, Any], steps: list[Any]) -> System:
    (tmp_path / "tables").mkdir()
    (tmp_path / "flows").mkdir()
    (tmp_path / "system.yaml").write_text(
        yaml.safe_dump({"id": "t", "kind": "system", "name": "T"})
    )
    for tid, extra in tables.items():
        data = {"id": tid, "kind": "table", "name": tid, "roll": "1d4"} | extra
        (tmp_path / "tables" / f"{tid}.yaml").write_text(yaml.safe_dump(data))
    flow = {"id": "f", "kind": "flow", "name": "F", "steps": steps}
    (tmp_path / "flows" / "f.yaml").write_text(yaml.safe_dump(flow))
    return SystemLoader().load(tmp_path)


def _roll(table: str, value: str) -> dict[str, Any]:
    return {
        "id": "roll",
        "type": "table_roll",
        "tables": [
            {
                "table": table,
                "actions": [{"set_value": {"path": "variables.x", "value": value}}],
            }
        ],
    }


SINGLE = {"entries": {1: "a", 2: "b"}}
MULTI = {"multiple_entries": True, "entries": {1: None, 2: "a", 3: ["a", "b"]}}


class TestResultFields:
    @pytest.mark.parametrize(
        ("template", "expected"),
        [
            ("{{ result.entry }}", {"entry"}),
            ("{{ result['entries'] | length }}", {"entries"}),
            ("{{ result.entry.name ~ result.entries[0] }}", {"entry", "entries"}),
            ("{{ result.roll_result.total }}", set()),
            ("{{ other.entry }}", set()),
        ],
    )
    def test_finds_result_fields(self, template: str, expected: set[str]) -> None:
        assert result_fields(template) == expected


class TestCandidateTables:
    def test_templated_reference_matches_by_wildcard(self) -> None:
        tables = {
            tid: TableDefinition(kind="table", name=tid, id=tid)
            for tid in ("warrior-armor", "rogue-armor", "gear")
        }
        found = candidate_tables("{{ inputs.class }}-armor", tables)
        assert sorted(t.id for t in found if t.id) == ["rogue-armor", "warrior-armor"]


class TestTableValidation:
    def test_list_entry_requires_the_declaration(self, tmp_path: Path) -> None:
        system = _system(tmp_path, {"t": {"entries": {1: ["a", "b"]}}}, [])
        assert system.validate() == [
            "Table 't': Entry '1' is a list; a table with list entries must "
            "declare `multiple_entries: true`"
        ]

    def test_list_elements_are_single_and_nonempty(self, tmp_path: Path) -> None:
        entries = {1: [], 2: ["a", None], 3: ["a", ["b"]]}
        system = _system(
            tmp_path, {"t": {"multiple_entries": True, "entries": entries}}, []
        )
        assert system.validate() == [
            "Table 't': Entry '1' is an empty list; use `null` for an entry that "
            "yields nothing",
            "Table 't': Entry '2[1]' must be a single entry, not null",
            "Table 't': Entry '3[1]' must be a single entry, not a list",
        ]

    def test_knave_helmets_and_shields_validates(self) -> None:
        system = SystemLoader().load(KNAVE)
        assert system.tables["helmets_and_shields"].multiple_entries is True
        assert system.validate() == []


class TestResultShapeAtLoad:
    def test_entry_on_ordinary_table_is_valid(self, tmp_path: Path) -> None:
        system = _system(tmp_path, {"t": SINGLE}, [_roll("t", "{{ result.entry }}")])
        assert system.validate() == []

    def test_entries_on_multiple_table_is_valid(self, tmp_path: Path) -> None:
        system = _system(tmp_path, {"t": MULTI}, [_roll("t", "{{ result.entries }}")])
        assert system.validate() == []

    def test_entry_on_multiple_table_fails_validation(self, tmp_path: Path) -> None:
        system = _system(tmp_path, {"t": MULTI}, [_roll("t", "{{ result.entry }}")])
        assert system.validate() == [
            "Flow 'f' step 'roll': table 't' declares `multiple_entries: true`, "
            "so its result is `result.entries`, not `result.entry`"
        ]

    def test_entries_on_ordinary_table_fails_validation(self, tmp_path: Path) -> None:
        system = _system(tmp_path, {"t": SINGLE}, [_roll("t", "{{ result.entries }}")])
        assert system.validate() == [
            "Flow 'f' step 'roll': table 't' yields one entry per roll, so its "
            "result is `result.entry`, not `result.entries`"
        ]

    def test_templated_table_checks_every_match(self, tmp_path: Path) -> None:
        tables = {"warrior-gear": SINGLE, "rogue-gear": MULTI}
        step = _roll("{{ inputs.cls }}-gear", "{{ result.entry }}")
        errors = _system(tmp_path, tables, [step]).validate()
        assert errors == [
            "Flow 'f' step 'roll': table 'rogue-gear' declares "
            "`multiple_entries: true`, so its result is `result.entries`, not "
            "`result.entry`"
        ]

    def test_reference_matching_no_table_fails(self, tmp_path: Path) -> None:
        step = _roll("{{ inputs.cls }}-gear", "{{ result.entry }}")
        errors = _system(tmp_path, {"t": SINGLE}, [step]).validate()
        assert errors == [
            "Flow 'f' step 'roll': no table matches '{{ inputs.cls }}-gear'"
        ]

    def test_multiple_table_cannot_source_a_choice(self, tmp_path: Path) -> None:
        step = {
            "id": "pick",
            "type": "player_choice",
            "choice_source": {"table": "t"},
        }
        errors = _system(tmp_path, {"t": MULTI}, [step]).validate()
        assert errors == [
            "Flow 'f' step 'pick': table 't' declares `multiple_entries: true` "
            "and cannot be the source of a player_choice"
        ]
