"""A `player_choice` choice's `id` must be a string, written as one.

The player answers a choice with its `id`, so the id the loader produces must
be exactly the one the author wrote. YAML 1.1 reads bare `yes`, `no`, `on`,
`off`, `true` and `false` as booleans; coercing those back with `str()` gives
`"True"` and — through a falsy-`or` fallback — `""`, silently. A missing `id`
became `""` the same way, and an undocumented `value` key stood in for `id`.
Each is now a load error naming the step.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml

from grimoire.loader import SystemLoader, SystemLoadError


def _load_choices(tmp_path: Path, choices: list[dict[str, Any]]) -> list[Any]:
    (tmp_path / "flows").mkdir()
    (tmp_path / "system.yaml").write_text(
        yaml.safe_dump({"id": "t", "kind": "system", "name": "T"})
    )
    flow = {
        "id": "f",
        "kind": "flow",
        "name": "F",
        "steps": [
            {"id": "ask", "type": "player_choice", "prompt": "?", "choices": choices}
        ],
    }
    (tmp_path / "flows" / "f.yaml").write_text(yaml.safe_dump(flow))
    return SystemLoader().load(tmp_path).flows["f"].steps[0].choices


def test_a_string_id_is_kept_exactly(tmp_path: Path) -> None:
    choices = _load_choices(
        tmp_path, [{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}]
    )

    assert [choice.id for choice in choices] == ["yes", "no"]


@pytest.mark.parametrize("bare", [True, False, 1, 0.5])
def test_a_non_string_id_is_rejected(tmp_path: Path, bare: Any) -> None:
    """`id: yes` reaches the loader as `True`, `id: no` as `False`."""
    with pytest.raises(SystemLoadError, match=r"Step 'ask'.*must be a string.*quote"):
        _load_choices(tmp_path, [{"id": bare, "label": "Pick"}])


def test_a_bare_yaml_boolean_is_rejected(tmp_path: Path) -> None:
    """End to end from the YAML text an author writes."""
    (tmp_path / "flows").mkdir()
    (tmp_path / "system.yaml").write_text("id: t\nkind: system\nname: T\n")
    (tmp_path / "flows" / "f.yaml").write_text(
        "id: f\nkind: flow\nname: F\nsteps:\n"
        "  - id: ask\n    type: player_choice\n    prompt: '?'\n"
        "    choices:\n      - id: no\n        label: No\n"
    )

    with pytest.raises(SystemLoadError, match="got False"):
        SystemLoader().load(tmp_path)


def test_a_missing_id_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemLoadError, match=r"Step 'ask'.*needs an `id`"):
        _load_choices(tmp_path, [{"label": "Pick"}])


def test_an_empty_id_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemLoadError, match=r"Step 'ask'.*must not be empty"):
        _load_choices(tmp_path, [{"id": "", "label": "Pick"}])


def test_value_does_not_stand_in_for_id(tmp_path: Path) -> None:
    with pytest.raises(SystemLoadError, match=r"`value` is not a choice field"):
        _load_choices(tmp_path, [{"value": "pick", "label": "Pick"}])
