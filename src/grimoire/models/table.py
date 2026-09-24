"""Table definition models for GRIMOIRE runner."""

import random
from dataclasses import dataclass, field
from typing import Any

PRIMITIVE_ENTRY_TYPES = {"str", "int", "float", "bool"}
REFERENCE_KEYS = {"id", "type", "generate"}


def _resolve(system: Any, key: Any, model_id: str, entry_id: Any) -> list[str]:
    """Check that `entry_id` is an entry of some compendium of `model_id`."""
    for compendium in system.compendiums.values():
        if compendium.model == model_id and entry_id in compendium.entries:
            return []
    return [f"Entry '{key}': {entry_id!r} is not in any '{model_id}' compendium"]


@dataclass
class TableEntry:
    """A single table entry with value and optional weight."""

    value: Any
    weight: int = 1


@dataclass
class TableDefinition:
    """Random table definition."""

    kind: str
    name: str
    id: str | None = None
    display_name: str | None = None
    version: str = "1.0"
    roll: str | None = None  # e.g., "1d10", "2d6"
    description: str | None = None
    entry_type: str = "str"  # Type hint for entries, defaults to "str"

    # Entries can be simple dict (roll_value -> result) or weighted
    entries: dict[int | str, Any] = field(default_factory=dict)

    def get_entry(self, roll_result: int | str) -> Any | None:
        """Get an entry by roll result."""
        return self.entries.get(roll_result)

    def get_all_entries(self) -> dict[int | str, Any]:
        """Get all entries."""
        return self.entries.copy()

    def get_random_entry(self, rng: random.Random | None = None) -> Any:
        """Get a random entry from the table."""
        if not self.entries:
            return None

        if rng is None:
            rng = random.Random()

        # For now, simple random choice (TODO: implement proper dice rolling)
        return rng.choice(list(self.entries.values()))

    def get_weighted_random_entry(
        self,
        weights: dict[int | str, int] | None = None,
        rng: random.Random | None = None,
    ) -> Any:
        """Get a weighted random entry from the table."""
        if not self.entries:
            return None

        if rng is None:
            rng = random.Random()

        if weights:
            # Use custom weights
            choices = []
            for key, value in self.entries.items():
                weight = weights.get(key, 1)
                choices.extend([value] * weight)
            return rng.choice(choices)
        else:
            # Equal weights
            return rng.choice(list(self.entries.values()))

    def get_entry_by_range(self, roll_value: int) -> Any | None:
        """Get entry by checking if roll_value falls within ranges."""
        # Handle range-based entries like "1-3": "result"
        for key, value in self.entries.items():
            if isinstance(key, str) and "-" in key:
                try:
                    start, end = map(int, key.split("-"))
                    if start <= roll_value <= end:
                        return value
                except ValueError:
                    continue
            elif isinstance(key, int) and key == roll_value:
                return value
            elif str(key) == str(roll_value):
                return value

        return None

    def validate(self) -> list[str]:
        """Validate the table definition and return any errors."""
        errors = []

        # Validate required fields
        if self.kind != "table":
            errors.append(f"Table kind must be 'table', got '{self.kind}'")
        if not self.name:
            errors.append("Table name is required")
        if not self.entries:
            errors.append("Table must have at least one entry")

        # The `roll` expression is not syntax-checked here: the loader has no
        # dice parser, and checking by rolling it drew real randomness at load.

        return errors

    def validate_with_system(self, system: Any) -> list[str]:
        """Validate the table, resolving its entries against the system.

        Follows spec/table_spec.md "Cross-References and Dynamic Generation":
        with a model `entry_type`, an entry is `null` (nothing), a string id
        looked up in a compendium of that model, a reference mapping
        (`{id, type, generate}`), or an inline instance of the model. With
        `entry_type: table`, every entry names another table.
        """
        errors = self.validate()
        if self.entry_type in PRIMITIVE_ENTRY_TYPES:
            return errors
        if self.entry_type == "table":
            for key, entry in self.entries.items():
                if entry is not None and entry not in system.tables:
                    errors.append(f"Entry '{key}' references unknown table {entry!r}")
            return errors
        if self.entry_type not in system.models:
            errors.append(f"entry_type '{self.entry_type}' references unknown model")
            return errors

        for key, entry in self.entries.items():
            if entry is None:
                continue
            if isinstance(entry, str):
                errors.extend(_resolve(system, key, self.entry_type, entry))
            elif isinstance(entry, dict) and set(entry) <= REFERENCE_KEYS:
                ref_type = entry.get("type", self.entry_type)
                if ref_type not in system.models:
                    errors.append(
                        f"Entry '{key}' references unknown model {ref_type!r}"
                    )
                elif "id" in entry:
                    errors.extend(_resolve(system, key, ref_type, entry["id"]))
            elif isinstance(entry, dict):
                model = system.models[self.entry_type]
                errors.extend(
                    f"Entry '{key}': {e}" for e in model.validate_instance(entry)
                )
            else:
                errors.append(
                    f"Entry '{key}' has entry_type '{self.entry_type}' but is "
                    f"a {type(entry).__name__}; expected null, an id, a "
                    "reference mapping or an inline instance"
                )
        return errors
