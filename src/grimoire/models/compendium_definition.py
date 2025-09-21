"""Compendium definition models for GRIMOIRE runner."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CompendiumDefinition:
    """Compendium definition containing collections of game content."""

    kind: str
    id: str  # Unique identifier for the compendium
    name: str  # Human-readable name
    model: str  # The model type that entries conform to
    entries: dict[str, dict[str, Any]] = field(default_factory=dict)

    def get_entry(self, entry_id: str) -> dict[str, Any] | None:
        """Get an entry by ID."""
        return self.entries.get(entry_id)

    def list_entries(self) -> list[str]:
        """Get a list of all entry IDs."""
        return list(self.entries.keys())

    def filter_entries(self, filter_func) -> dict[str, dict[str, Any]]:
        """Filter entries based on a function."""
        return {
            entry_id: entry_data
            for entry_id, entry_data in self.entries.items()
            if filter_func(entry_data)
        }

    def search_entries(
        self, search_term: str, fields: list[str] | None = None
    ) -> dict[str, dict[str, Any]]:
        """Search entries by text in specified fields (or all string fields)."""
        search_term = search_term.lower()
        results = {}

        for entry_id, entry_data in self.entries.items():
            if self._entry_matches_search(entry_data, search_term, fields):
                results[entry_id] = entry_data

        return results

    def _entry_matches_search(
        self,
        entry_data: dict[str, Any],
        search_term: str,
        fields: list[str] | None = None,
    ) -> bool:
        """Check if an entry matches the search term."""

        def search_in_value(value: Any) -> bool:
            if isinstance(value, str):
                return search_term in value.lower()
            elif isinstance(value, dict):
                return any(search_in_value(v) for v in value.values())
            elif isinstance(value, list):
                return any(search_in_value(item) for item in value)
            return False

        if fields:
            # Search only in specified fields
            for field in fields:
                if field in entry_data and search_in_value(entry_data[field]):
                    return True
        else:
            # Search in all fields
            return search_in_value(entry_data)

        return False

    def validate(self) -> list[str]:
        """Validate the compendium definition and return any errors."""
        errors = []

        # Validate required fields
        if self.kind != "compendium":
            errors.append(f"Compendium kind must be 'compendium', got '{self.kind}'")
        if not self.id:
            errors.append("Compendium id is required")
        if not self.name:
            errors.append("Compendium name is required")
        if not self.model:
            errors.append("Compendium model is required")

        # Validate entry IDs are unique (they are by dict nature, but check for empty)
        if not self.entries:
            errors.append("Compendium must have at least one entry")

        # TODO: Validate entries against model definition

        return errors
