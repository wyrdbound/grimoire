"""System definition models for GRIMOIRE runner."""

from dataclasses import dataclass, field
from pathlib import Path

from .compendium import CompendiumDefinition
from .flow.flow import FlowDefinition
from .model import ModelDefinition
from .prompt import PromptDefinition
from .source import SourceDefinition
from .table import TableDefinition


@dataclass
class CurrencyDenomination:
    """A currency denomination definition."""

    name: str
    symbol: str
    value: int
    weight: float | None = None


@dataclass
class Currency:
    """Currency system definition."""

    base_unit: str
    denominations: dict[str, CurrencyDenomination] = field(default_factory=dict)


@dataclass
class Credits:
    """Attribution and licensing information."""

    author: str | None = None
    license: str | None = None
    publisher: str | None = None
    source_url: str | None = None


@dataclass
class System:
    """Complete GRIMOIRE system definition."""

    # Required fields
    id: str
    name: str
    kind: str = "system"

    # Optional metadata
    description: str | None = None
    version: str | None = None
    default_source: str | None = None

    # System configuration
    currency: Currency | None = None
    credits: Credits | None = None

    # Content collections
    models: dict[str, ModelDefinition] = field(default_factory=dict)
    flows: dict[str, FlowDefinition] = field(default_factory=dict)
    compendiums: dict[str, CompendiumDefinition] = field(default_factory=dict)
    tables: dict[str, TableDefinition] = field(default_factory=dict)
    sources: dict[str, SourceDefinition] = field(default_factory=dict)
    prompts: dict[str, PromptDefinition] = field(default_factory=dict)

    # Internal fields
    _system_path: Path | None = field(default=None, repr=False)

    def get_model(self, model_id: str) -> ModelDefinition | None:
        """Get a model definition by ID."""
        return self.models.get(model_id)

    def get_flow(self, flow_id: str) -> FlowDefinition | None:
        """Get a flow definition by ID."""
        return self.flows.get(flow_id)

    def get_compendium(self, compendium_id: str) -> CompendiumDefinition | None:
        """Get a compendium definition by ID."""
        return self.compendiums.get(compendium_id)

    def get_table(self, table_id: str) -> TableDefinition | None:
        """Get a table definition by ID."""
        return self.tables.get(table_id)

    def get_source(self, source_id: str) -> SourceDefinition | None:
        """Get a source definition by ID."""
        return self.sources.get(source_id)

    def get_prompt(self, prompt_id: str) -> PromptDefinition | None:
        """Get a prompt definition by ID."""
        return self.prompts.get(prompt_id)

    def list_flows(self) -> list[str]:
        """Get a list of all available flow IDs."""
        return list(self.flows.keys())

    def list_models(self) -> list[str]:
        """Get a list of all available model IDs."""
        return list(self.models.keys())

    def list_compendiums(self) -> list[str]:
        """Get a list of all available compendium IDs."""
        return list(self.compendiums.keys())

    def list_tables(self) -> list[str]:
        """Get a list of all available table IDs."""
        return list(self.tables.keys())

    def validate(self) -> list[str]:
        """Validate the system definition and return any errors."""
        errors = []

        # Validate required fields
        if not self.id:
            errors.append("System ID is required")
        if not self.name:
            errors.append("System name is required")
        if self.kind != "system":
            errors.append(f"System kind must be 'system', got '{self.kind}'")

        # Validate references
        if self.default_source and self.default_source not in self.sources:
            errors.append(f"Default source '{self.default_source}' not found")

        # Validate currency denominations
        if self.currency:
            for denom_id, denom in self.currency.denominations.items():
                if denom.value <= 0:
                    errors.append(
                        f"Currency denomination '{denom_id}' must have positive value"
                    )

        return errors
