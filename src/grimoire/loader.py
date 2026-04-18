"""SystemLoader — loads a GRIMOIRE system directory into a System object."""

from pathlib import Path
from typing import Any

import yaml

from grimoire.models.compendium_definition import CompendiumDefinition
from grimoire.models.flow import (
    ChoiceDefinition,
    DiceSequenceDefinition,
    FlowDefinition,
    LLMSettingsDefinition,
    LLMValidationDefinition,
    StepDefinition,
    StepType,
    TableRollDefinition,
    VariableDefinition,
)
from grimoire.models.model_definition import ModelDefinition, ValidationRule
from grimoire.models.prompt import PromptDefinition
from grimoire.models.source import SourceDefinition
from grimoire.models.system import Credits, Currency, CurrencyDenomination, System
from grimoire.models.table import TableDefinition


class SystemLoadError(Exception):
    """Raised when a GRIMOIRE system directory cannot be loaded."""


class SystemLoader:
    """Loads a GRIMOIRE system directory into a :class:`System` instance.

    Usage::

        loader = SystemLoader()
        system = loader.load(Path("systems/knave_1e"))
        errors = system.validate()
    """

    def load(self, system_path: Path) -> System:
        """Load a complete system from a directory.

        Args:
            system_path: Path to the system directory (must contain system.yaml).

        Returns:
            A fully populated :class:`System` instance.

        Raises:
            SystemLoadError: If the path does not exist, system.yaml is missing,
                or any YAML file is malformed.
        """
        if not system_path.exists():
            raise SystemLoadError(f"System path does not exist: {system_path}")

        system_yaml = system_path / "system.yaml"
        if not system_yaml.exists():
            raise SystemLoadError(f"Missing system.yaml in {system_path}")

        data = self._read_yaml(system_yaml)
        system = self._parse_system(data)
        system._system_path = system_path

        self._load_models(system, system_path / "models")
        self._load_tables(system, system_path / "tables")
        self._load_compendiums(system, system_path / "compendiums")
        self._load_flows(system, system_path / "flows")
        self._load_prompts(system, system_path / "prompts")
        self._load_sources(system, system_path / "sources")

        return system

    # ------------------------------------------------------------------
    # YAML helpers
    # ------------------------------------------------------------------

    def _read_yaml(self, path: Path) -> dict[str, Any]:
        try:
            with path.open(encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            raise SystemLoadError(f"Invalid YAML in {path}: {exc}") from exc

    # ------------------------------------------------------------------
    # System
    # ------------------------------------------------------------------

    def _parse_system(self, data: dict[str, Any]) -> System:
        currency = None
        if "currency" in data:
            currency = self._parse_currency(data["currency"])

        credits_obj = None
        if "credits" in data:
            credits_obj = self._parse_credits(data["credits"])

        return System(
            id=data["id"],
            name=data["name"],
            kind=data.get("kind", "system"),
            description=data.get("description"),
            version=str(data["version"]) if "version" in data else None,
            default_source=data.get("default_source"),
            currency=currency,
            credits=credits_obj,
        )

    def _parse_currency(self, data: dict[str, Any]) -> Currency:
        denominations: dict[str, CurrencyDenomination] = {}
        for denom_id, denom_data in data.get("denominations", {}).items():
            denominations[denom_id] = CurrencyDenomination(
                name=denom_data["name"],
                symbol=denom_data["symbol"],
                value=denom_data["value"],
                weight=denom_data.get("weight"),
            )
        return Currency(base_unit=data["base_unit"], denominations=denominations)

    def _parse_credits(self, data: dict[str, Any]) -> Credits:
        return Credits(
            author=data.get("author"),
            license=data.get("license"),
            publisher=data.get("publisher"),
            source_url=data.get("source_url"),
        )

    # ------------------------------------------------------------------
    # Models
    # ------------------------------------------------------------------

    def _load_models(self, system: System, models_dir: Path) -> None:
        if not models_dir.exists():
            return
        for yaml_file in sorted(models_dir.glob("*.yaml")):
            try:
                data = self._read_yaml(yaml_file)
                model = self._parse_model(data)
                system.models[model.id] = model
            except SystemLoadError:
                raise
            except Exception as exc:
                raise SystemLoadError(
                    f"Failed to load model {yaml_file}: {exc}"
                ) from exc

    def _parse_model(self, data: dict[str, Any]) -> ModelDefinition:
        validations = [
            ValidationRule(
                expression=v["expression"],
                message=v.get("message", "Validation failed"),
            )
            for v in data.get("validations", [])
        ]
        return ModelDefinition(
            id=data["id"],
            name=data["name"],
            kind=data.get("kind", "model"),
            description=data.get("description"),
            version=int(data.get("version", 1)),
            extends=data.get("extends", []),
            attributes=data.get("attributes", {}),
            validations=validations,
        )

    # ------------------------------------------------------------------
    # Tables
    # ------------------------------------------------------------------

    def _load_tables(self, system: System, tables_dir: Path) -> None:
        if not tables_dir.exists():
            return
        for yaml_file in sorted(tables_dir.rglob("*.yaml")):
            try:
                data = self._read_yaml(yaml_file)
                table = self._parse_table(data)
                if table.id:
                    system.tables[table.id] = table
            except SystemLoadError:
                raise
            except Exception as exc:
                raise SystemLoadError(
                    f"Failed to load table {yaml_file}: {exc}"
                ) from exc

    def _parse_table(self, data: dict[str, Any]) -> TableDefinition:
        # Preserve original entry keys as strings so range-style keys like
        # "1-3" remain intact; YAML may parse pure-integer keys as int.
        entries: dict[int | str, Any] = {
            k: v for k, v in data.get("entries", {}).items()
        }
        return TableDefinition(
            kind=data.get("kind", "table"),
            name=data["name"],
            id=data.get("id"),
            display_name=data.get("display_name"),
            version=str(data.get("version", "1.0")),
            roll=str(data["roll"]) if "roll" in data else None,
            description=data.get("description"),
            entry_type=data.get("entry_type", "str"),
            entries=entries,
        )

    # ------------------------------------------------------------------
    # Compendiums
    # ------------------------------------------------------------------

    def _load_compendiums(self, system: System, compendiums_dir: Path) -> None:
        if not compendiums_dir.exists():
            return
        for yaml_file in sorted(compendiums_dir.rglob("*.yaml")):
            try:
                data = self._read_yaml(yaml_file)
                compendium = self._parse_compendium(data)
                system.compendiums[compendium.id] = compendium
            except SystemLoadError:
                raise
            except Exception as exc:
                raise SystemLoadError(
                    f"Failed to load compendium {yaml_file}: {exc}"
                ) from exc

    def _parse_compendium(self, data: dict[str, Any]) -> CompendiumDefinition:
        entries_raw = data.get("entries", {})
        # Handle list format (e.g. wyrdbound): list of dicts each containing
        # an 'id' field — convert to the canonical dict-keyed format.
        if isinstance(entries_raw, list):
            entries: dict[str, dict[str, Any]] = {}
            for entry in entries_raw:
                entry_copy = dict(entry)
                entry_id = str(entry_copy.pop("id"))
                entries[entry_id] = entry_copy
        else:
            entries = {str(k): v for k, v in entries_raw.items()}

        return CompendiumDefinition(
            kind=data.get("kind", "compendium"),
            id=data["id"],
            name=data["name"],
            model=data["model"],
            entries=entries,
        )

    # ------------------------------------------------------------------
    # Flows
    # ------------------------------------------------------------------

    def _load_flows(self, system: System, flows_dir: Path) -> None:
        if not flows_dir.exists():
            return
        for yaml_file in sorted(flows_dir.rglob("*.yaml")):
            try:
                data = self._read_yaml(yaml_file)
                flow = self._parse_flow(data)
                system.flows[flow.id] = flow
            except SystemLoadError:
                raise
            except Exception as exc:
                raise SystemLoadError(
                    f"Failed to load flow {yaml_file}: {exc}"
                ) from exc

    def _parse_flow(self, data: dict[str, Any]) -> FlowDefinition:
        version_raw = data.get("version")
        return FlowDefinition(
            id=data["id"],
            name=data["name"],
            # YAML uses 'kind', but FlowDefinition uses 'type'
            type=data.get("kind", "flow"),
            description=data.get("description"),
            version=str(version_raw) if version_raw is not None else None,
            inputs=[self._parse_variable(v) for v in data.get("inputs", [])],
            outputs=[self._parse_variable(v) for v in data.get("outputs", [])],
            variables=[self._parse_variable(v) for v in data.get("variables", [])],
            steps=[self._parse_step(s) for s in data.get("steps", [])],
            resume_points=data.get("resume_points", []),
        )

    def _parse_variable(self, data: dict[str, Any]) -> VariableDefinition:
        return VariableDefinition(
            id=data["id"],
            type=data.get("type", "unknown"),
            description=data.get("description"),
            default=data.get("default"),
            enum=data.get("enum"),
        )

    def _parse_step(self, data: dict[str, Any]) -> StepDefinition:
        type_str = data.get("type", "")
        try:
            step_type: StepType | None = StepType(type_str)
        except ValueError:
            step_type = None

        choices = [self._parse_choice(c) for c in data.get("choices", [])]

        tables = [
            TableRollDefinition(
                table=t["table"],
                count=t.get("count", 1),
                actions=t.get("actions", []),
            )
            for t in data.get("tables", [])
        ]

        sequence: DiceSequenceDefinition | None = None
        if "sequence" in data:
            sd = data["sequence"]
            sequence = DiceSequenceDefinition(
                items=sd["items"],
                roll=sd["roll"],
                actions=sd.get("actions"),
            )

        llm_settings: LLMSettingsDefinition | None = None
        if "llm_settings" in data:
            ls = data["llm_settings"]
            llm_settings = LLMSettingsDefinition(
                provider=ls.get("provider", "anthropic"),
                model=ls.get("model", "claude-3-haiku"),
                max_tokens=ls.get("max_tokens", 200),
                temperature=ls.get("temperature", 0.7),
            )

        validation: LLMValidationDefinition | None = None
        if "validation" in data:
            vd = data["validation"]
            validation = LLMValidationDefinition(
                type=vd["type"],
                schema=vd.get("schema"),
                max_attempts=vd.get("max_attempts", 3),
                cleanup_enabled=vd.get("cleanup_enabled", True),
                on_failure=vd.get("on_failure", "continue"),
                fallback_value=vd.get("fallback_value"),
            )

        return StepDefinition(
            id=data["id"],
            name=data.get("name"),
            type=step_type,
            actions=data.get("actions", []),
            next_step=data.get("next_step"),
            prompt=data.get("prompt"),
            condition=data.get("condition"),
            result_message=data.get("result_message"),
            output=data.get("output"),
            roll=data.get("roll"),
            sequence=sequence,
            choices=choices,
            choice_source=data.get("choice_source"),
            pre_actions=data.get("pre_actions", []),
            post_actions=data.get("post_actions", []),
            tables=tables,
            prompt_id=data.get("prompt_id"),
            prompt_data=data.get("prompt_data") or {},
            llm_settings=llm_settings,
            validation=validation,
            # conditional_branch: YAML uses 'if'/'then'/'else'
            if_condition=data.get("if"),
            then_actions=data.get("then") or [],
            else_actions=data.get("else"),
            flow=data.get("flow"),
            inputs=data.get("inputs") or {},
            result=data.get("result"),
            generator=data.get("generator"),
            settings=data.get("settings") or {},
        )

    def _parse_choice(self, data: dict[str, Any]) -> ChoiceDefinition:
        # Some YAML files use 'value' instead of 'id' for the choice identifier
        choice_id = data.get("id") or data.get("value", "")
        return ChoiceDefinition(
            id=str(choice_id),
            label=data.get("label", ""),
            next_step=data.get("next_step"),
            actions=data.get("actions", []),
            reset_outputs=data.get("reset_outputs", False),
            description=data.get("description"),
        )

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------

    def _load_prompts(self, system: System, prompts_dir: Path) -> None:
        if not prompts_dir.exists():
            return
        for yaml_file in sorted(prompts_dir.glob("*.yaml")):
            try:
                data = self._read_yaml(yaml_file)
                prompt = self._parse_prompt(data)
                prompt_id = prompt.id or prompt.name
                system.prompts[prompt_id] = prompt
            except SystemLoadError:
                raise
            except Exception as exc:
                raise SystemLoadError(
                    f"Failed to load prompt {yaml_file}: {exc}"
                ) from exc

    def _parse_prompt(self, data: dict[str, Any]) -> PromptDefinition:
        return PromptDefinition(
            kind=data.get("kind", "prompt"),
            name=data["name"],
            prompt_template=data["prompt_template"],
            id=data.get("id"),
            description=data.get("description"),
            version=str(data.get("version", "1.0")),
            llm=data.get("llm"),  # PromptDefinition.__post_init__ converts dict
        )

    # ------------------------------------------------------------------
    # Sources
    # ------------------------------------------------------------------

    def _load_sources(self, system: System, sources_dir: Path) -> None:
        if not sources_dir.exists():
            return
        for yaml_file in sorted(sources_dir.glob("*.yaml")):
            try:
                data = self._read_yaml(yaml_file)
                source = self._parse_source(data)
                source_id = source.id or source.name
                system.sources[source_id] = source
            except SystemLoadError:
                raise
            except Exception as exc:
                raise SystemLoadError(
                    f"Failed to load source {yaml_file}: {exc}"
                ) from exc

    def _parse_source(self, data: dict[str, Any]) -> SourceDefinition:
        return SourceDefinition(
            kind=data.get("kind", "source"),
            name=data["name"],
            id=data.get("id"),
            display_name=data.get("display_name"),
            edition=data.get("edition"),
            default=data.get("default"),
            publisher=data.get("publisher"),
            description=data.get("description"),
            source_url=data.get("source_url"),
            version=str(data.get("version", "1.0")),
        )
