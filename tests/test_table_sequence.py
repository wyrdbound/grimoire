"""The `table_sequence` step, and `count` leaving `table_roll`."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from grimoire.loader import SystemLoader, SystemLoadError
from grimoire.models.flow import StepType
from grimoire.models.system import System


def _system(tmp_path: Path, steps: list[Any], multiple: bool = False) -> System:
    (tmp_path / "tables").mkdir()
    (tmp_path / "flows").mkdir()
    (tmp_path / "system.yaml").write_text(
        yaml.safe_dump({"id": "t", "kind": "system", "name": "T"})
    )
    table = {"id": "gems", "kind": "table", "name": "Gems", "roll": "1d4"}
    table |= (
        {"multiple_entries": True, "entries": {1: ["a", "b"], 2: "c"}}
        if multiple
        else {"entries": {1: "a", 2: "b"}}
    )
    (tmp_path / "tables" / "gems.yaml").write_text(yaml.safe_dump(table))
    flow = {"id": "f", "kind": "flow", "name": "F", "steps": steps}
    (tmp_path / "flows" / "f.yaml").write_text(yaml.safe_dump(flow))
    return SystemLoader().load(tmp_path)


def _seq(sequence: dict[str, Any], **step: Any) -> dict[str, Any]:
    return {"id": "gems", "type": "table_sequence", "sequence": sequence} | step


APPEND = [{"append_value": {"path": "outputs.hoard", "value": "{{ result.entry }}"}}]


class TestParsing:
    def test_count_sequence_is_parsed(self, tmp_path: Path) -> None:
        step = (
            _system(tmp_path, [_seq({"table": "gems", "count": 3, "actions": APPEND})])
            .flows["f"]
            .steps[0]
        )
        assert step.type == StepType.TABLE_SEQUENCE
        assert step.table_sequence is not None
        assert (step.table_sequence.table, step.table_sequence.count) == ("gems", 3)
        assert step.table_sequence.actions == APPEND

    @pytest.mark.parametrize(
        "sequence",
        [
            {"table": "gems", "count": "{{ variables.n }}"},
            {"table": "gems", "count": 0},
            {"table": "gems", "items": ["alice", "bob"]},
            {"table": "gems", "items": "{{ inputs.party }}"},
        ],
    )
    def test_valid_sequences(self, tmp_path: Path, sequence: dict[str, Any]) -> None:
        assert _system(tmp_path, [_seq(sequence)]).validate() == []

    @pytest.mark.parametrize(
        ("sequence", "message"),
        [
            (None, "needs a `sequence`"),
            ({"count": 2}, "`table` is required"),
            ({"table": "gems"}, "exactly one of `count` and `items`"),
            ({"table": "gems", "count": 1, "items": ["a"]}, "exactly one of"),
            ({"table": "gems", "count": -1}, "`count` must be"),
            ({"table": "gems", "count": "3"}, "`count` must be"),
            ({"table": "gems", "count": True}, "`count` must be"),
            ({"table": "gems", "items": []}, "`items` must be"),
        ],
    )
    def test_invalid_sequences_fail_to_load(
        self, tmp_path: Path, sequence: Any, message: str
    ) -> None:
        with pytest.raises(SystemLoadError, match=message):
            _system(tmp_path, [_seq(sequence)])

    def test_count_on_table_roll_is_rejected(self, tmp_path: Path) -> None:
        step = {
            "id": "r",
            "type": "table_roll",
            "tables": [{"table": "gems", "count": 2}],
        }
        with pytest.raises(SystemLoadError, match="Use a `table_sequence` step"):
            _system(tmp_path, [step])


class TestResultShapeAtLoad:
    def test_entry_on_ordinary_table(self, tmp_path: Path) -> None:
        steps = [_seq({"table": "gems", "count": 2, "actions": APPEND})]
        assert _system(tmp_path, steps).validate() == []

    def test_entry_on_multiple_table_fails(self, tmp_path: Path) -> None:
        steps = [_seq({"table": "gems", "count": 2, "actions": APPEND})]
        assert _system(tmp_path, steps, multiple=True).validate() == [
            "Flow 'f' step 'gems': table 'gems' declares `multiple_entries: true`, "
            "so its result is `result.entries`, not `result.entry`"
        ]

    def test_unknown_table_fails(self, tmp_path: Path) -> None:
        steps = [_seq({"table": "rubies", "count": 1})]
        assert _system(tmp_path, steps).validate() == [
            "Flow 'f' step 'gems': no table matches 'rubies'"
        ]

    def test_step_actions_cannot_read_result(self, tmp_path: Path) -> None:
        steps = [
            _seq(
                {"table": "gems", "count": 2},
                actions=[{"display_message": "Last: {{ result.entry }}"}],
            )
        ]
        assert _system(tmp_path, steps).validate() == [
            "Flow 'f' step 'gems': `result` is only available in the sequence's "
            "own actions, which run once per roll; the step's actions run once, "
            "after every roll"
        ]
