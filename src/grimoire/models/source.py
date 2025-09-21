"""Source definition models for GRIMOIRE runner."""

from dataclasses import dataclass


@dataclass
class SourceDefinition:
    """Source material definition for attribution and licensing."""

    kind: str
    name: str
    id: str | None = None
    display_name: str | None = None
    edition: str | None = None
    default: bool | None = None
    publisher: str | None = None
    description: str | None = None
    source_url: str | None = None
    version: str = "1.0"

    def validate(self) -> list[str]:
        """Validate the source definition and return any errors."""
        errors = []

        # Validate required fields
        if self.kind != "source":
            errors.append(f"Source kind must be 'source', got '{self.kind}'")
        if not self.name:
            errors.append("Source name is required")

        return errors
