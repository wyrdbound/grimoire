"""The quickstart's character model has a complete spell_slots (wyrdbound F51).

`character_creation` writes `spell_slots.max` and `spell_slots.current` only on
the mage branch, but `character` validates its output in full for every class.
`max` carries `default: 0`; `current` did not, so for a non-mage the required
`spell_slots.current` was never present and the output failed its own
validation ("Required field 'spell_slots.current' is missing").

The fix is a `default: 0` on `current`, matching `max`. This test is static: it
checks the declaration, and it is what the grimoire suite can see without an
engine.
"""

from pathlib import Path

import yaml

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"
CHARACTER = SYSTEMS_DIR / "wyrdbound-quickstart-1e" / "models" / "character.yaml"


def _attr(model: dict, path: str) -> dict:
    node = model["attributes"]
    for part in path.split("."):
        node = node[part]
    return node


def test_spell_slots_current_has_a_default() -> None:
    model = yaml.safe_load(CHARACTER.read_text())
    current = _attr(model, "spell_slots.current")

    assert "default" in current, (
        "spell_slots.current needs a default so a non-mage's validated output "
        "has the field (wyrdbound F51)"
    )
    assert current["default"] == 0


def test_spell_slots_current_default_matches_max() -> None:
    """Both slots start at zero; the default must not be null (F7 forbids
    `default: null`, and the model's own validation compares the two)."""
    model = yaml.safe_load(CHARACTER.read_text())

    assert _attr(model, "spell_slots.max")["default"] == 0
    assert _attr(model, "spell_slots.current")["default"] == 0
