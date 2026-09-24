"""Step output naming (`result`), completion `final_message`, and table lookups."""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from grimoire.loader import SystemLoader, SystemLoadError

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"
SYSTEMS = ["knave-1e", "wyrdbound-quickstart-1e"]
PRIMITIVES = {"str", "int", "float", "bool"}
RETIRED = re.compile(r"\{\{[^}]*\b(choice|choice_entry|results|llm_result)\b")


def _load_one_step(tmp_path: Path, step: dict[str, Any]) -> Any:
    (tmp_path / "flows").mkdir()
    (tmp_path / "system.yaml").write_text(
        yaml.safe_dump({"id": "t", "kind": "system", "name": "T"})
    )
    flow = {"id": "f", "kind": "flow", "name": "F", "steps": [step]}
    (tmp_path / "flows" / "f.yaml").write_text(yaml.safe_dump(flow))
    return SystemLoader().load(tmp_path).flows["f"].steps[0]


def test_completion_final_message_is_parsed(tmp_path: Path) -> None:
    step = _load_one_step(
        tmp_path, {"id": "end", "type": "completion", "final_message": "Done"}
    )
    assert step.final_message == "Done"


def test_result_message_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemLoadError, match="renamed `final_message`"):
        _load_one_step(
            tmp_path, {"id": "end", "type": "completion", "result_message": "x"}
        )


def test_prompt_on_completion_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemLoadError, match="takes `final_message`"):
        _load_one_step(tmp_path, {"id": "end", "type": "completion", "prompt": "x"})


@pytest.mark.parametrize("system", SYSTEMS)
def test_no_retired_result_names(system: str) -> None:
    for path in (SYSTEMS_DIR / system / "flows").rglob("*.yaml"):
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            assert not RETIRED.search(line), f"{path}:{n}: {line.strip()}"


@pytest.mark.parametrize(
    "system",
    [
        pytest.param(
            "knave-1e",
            marks=pytest.mark.xfail(
                strict=True,
                reason=(
                    "armor and helmets_and_shields use the string 'none' for "
                    "'no armor'; the spec has no way for a model-typed table "
                    "to yield nothing. Open finding, awaiting a decision."
                ),
            ),
        ),
        "wyrdbound-quickstart-1e",
    ],
)
def test_model_typed_table_entries_resolve_in_a_compendium(system: str) -> None:
    loaded = SystemLoader().load(SYSTEMS_DIR / system)
    by_model: dict[str, set[str]] = {}
    for comp in loaded.compendiums.values():
        by_model.setdefault(comp.model, set()).update(comp.entries)
    for table in loaded.tables.values():
        if table.entry_type in PRIMITIVES or table.entry_type == "table":
            continue
        for key, entry in table.entries.items():
            if isinstance(entry, str):
                assert entry in by_model.get(table.entry_type, set()), (
                    f"{table.id}[{key}] = {entry!r}: no {table.entry_type} "
                    "compendium entry"
                )
