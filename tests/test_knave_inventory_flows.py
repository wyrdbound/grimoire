"""Knave's inventory flows do not shadow inputs or truncate the character.

Three defects lived in `add_items_to_character` (wyrdbound F53, F54, F55), all
found while preparing `roll_starting_gear` to be re-enabled:

- **F53** — `inputs.items` resolves to the *dict method*, not the declared
  input, because Jinja2 prefers a real attribute of the mapping over its key.
  A flow that declares an input named like a dict method must read it with
  subscript syntax (`inputs['items']`).
- **F54** — `items | map(attribute='display_name')`, but the `item` model
  declares `name`.
- **F55** — the flow wrote `outputs.character.inventory` without first copying
  `inputs.character` into `outputs.character`, so its output was a model
  holding *only* an inventory. The caller then replaces its character with it,
  silently discarding every other attribute.

These are static checks — what this suite can see without a flow engine.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from grimoire.loader import SystemLoader

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"
KNAVE_DIR = SYSTEMS_DIR / "knave-1e"
ADD_ITEMS = KNAVE_DIR / "flows" / "inventory" / "add_items_to_character.yaml"

#: Python `dict` attributes that a flow input id could collide with. Reading
#: `inputs.<one of these>` yields the method, not the input.
DICT_ATTRIBUTES = (
    "items",
    "keys",
    "values",
    "get",
    "pop",
    "popitem",
    "setdefault",
    "update",
    "clear",
    "copy",
    "fromkeys",
)


def _flow_files() -> list[Path]:
    return sorted(KNAVE_DIR.glob("flows/**/*.yaml"))


@pytest.mark.parametrize("path", _flow_files(), ids=lambda p: p.name)
def test_no_flow_reads_an_input_through_a_dict_attribute(path: Path) -> None:
    """F53: `inputs.items` (or any dict method) is the method, not the input."""
    text = path.read_text()
    pattern = re.compile(r"inputs\.(" + "|".join(DICT_ATTRIBUTES) + r")\b")
    offenders = sorted({match.group(0) for match in pattern.finditer(text)})

    assert offenders == [], (
        f"{path.relative_to(SYSTEMS_DIR)} reads {offenders} — a dict attribute, "
        "not the declared input; use inputs['name'] (wyrdbound F53)"
    )


def test_add_items_does_not_read_a_nonexistent_display_name() -> None:
    """F54: the item model has `name`, not `display_name`."""
    text = ADD_ITEMS.read_text()

    assert "display_name" not in text


def test_add_items_copies_the_input_character_before_writing_to_it() -> None:
    """F55: `outputs.character` must start as the input character, or the
    caller's `result.character` replaces the character with a bare inventory."""
    flow = yaml.safe_load(ADD_ITEMS.read_text())
    actions = flow["steps"][0]["actions"]
    paths = [action["set_value"]["path"] for action in actions if "set_value" in action]

    assert "outputs.character" in paths, (
        "add_items_to_character must assign `outputs.character = "
        "{{ inputs.character }}` before touching outputs.character.inventory "
        "(wyrdbound F55)"
    )
    assert paths.index("outputs.character") < paths.index("outputs.character.inventory")


def test_the_system_still_loads_and_validates() -> None:
    assert SystemLoader().load(KNAVE_DIR).validate() == []
