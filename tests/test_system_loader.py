"""Tests for SystemLoader — loads a GRIMOIRE system directory into a System."""

from pathlib import Path

import pytest

from grimoire.loader import SystemLoader, SystemLoadError
from grimoire.models.system import System

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"
KNAVE_DIR = SYSTEMS_DIR / "knave-1e"
WYRDBOUND_DIR = SYSTEMS_DIR / "wyrdbound-quickstart-1e"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def loader() -> SystemLoader:
    return SystemLoader()


@pytest.fixture
def knave(loader: SystemLoader) -> System:
    return loader.load(KNAVE_DIR)


@pytest.fixture
def wyrdbound(loader: SystemLoader) -> System:
    return loader.load(WYRDBOUND_DIR)


# ---------------------------------------------------------------------------
# Basic loading
# ---------------------------------------------------------------------------


class TestSystemLoaderBasicLoading:
    def test_load_returns_system(self, loader: SystemLoader) -> None:
        system = loader.load(KNAVE_DIR)
        assert isinstance(system, System)

    def test_load_knave_id(self, knave: System) -> None:
        assert knave.id == "knave_1e"

    def test_load_knave_name(self, knave: System) -> None:
        assert knave.name == "Knave (1st Edition)"

    def test_load_knave_kind(self, knave: System) -> None:
        assert knave.kind == "system"

    def test_load_wyrdbound_id(self, wyrdbound: System) -> None:
        assert wyrdbound.id == "wyrdbound-quickstart-1e"

    def test_load_wyrdbound_name(self, wyrdbound: System) -> None:
        assert "Wyrdbound" in wyrdbound.name

    def test_nonexistent_path_raises(self, loader: SystemLoader) -> None:
        with pytest.raises(SystemLoadError):
            loader.load(Path("/nonexistent/path"))

    def test_missing_system_yaml_raises(
        self, loader: SystemLoader, tmp_path: Path
    ) -> None:
        with pytest.raises(SystemLoadError):
            loader.load(tmp_path)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TestSystemLoaderModels:
    def test_knave_loads_all_models(self, knave: System) -> None:
        # 8 model YAML files in systems/knave_1e/models/
        assert len(knave.models) == 8

    def test_knave_has_character_model(self, knave: System) -> None:
        assert "character" in knave.models

    def test_knave_has_item_model(self, knave: System) -> None:
        assert "item" in knave.models

    def test_knave_character_model_name(self, knave: System) -> None:
        assert knave.models["character"].name == "Knave"

    def test_wyrdbound_loads_all_models(self, wyrdbound: System) -> None:
        # 7 model YAML files in systems/wyrdbound-quickstart-1e/models/
        assert len(wyrdbound.models) == 7

    def test_wyrdbound_has_character_model(self, wyrdbound: System) -> None:
        assert "character" in wyrdbound.models


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


class TestSystemLoaderTables:
    def test_knave_loads_all_tables(self, knave: System) -> None:
        # 19 table YAML files in systems/knave_1e/tables/ (recursive)
        assert len(knave.tables) == 19

    def test_knave_has_armor_table(self, knave: System) -> None:
        assert "armor" in knave.tables

    def test_knave_armor_table_kind(self, knave: System) -> None:
        assert knave.tables["armor"].kind == "table"

    def test_knave_armor_table_has_entries(self, knave: System) -> None:
        assert len(knave.tables["armor"].entries) > 0

    def test_wyrdbound_loads_all_tables(self, wyrdbound: System) -> None:
        # 14 table YAML files in systems/wyrdbound-quickstart-1e/tables/ (recursive)
        assert len(wyrdbound.tables) == 14


# ---------------------------------------------------------------------------
# Compendiums
# ---------------------------------------------------------------------------


class TestSystemLoaderCompendiums:
    def test_knave_loads_all_compendiums(self, knave: System) -> None:
        # 9 compendium YAML files in systems/knave_1e/compendiums/ (recursive)
        assert len(knave.compendiums) == 9

    def test_knave_has_melee_compendium(self, knave: System) -> None:
        assert "melee" in knave.compendiums

    def test_knave_melee_compendium_model(self, knave: System) -> None:
        assert knave.compendiums["melee"].model == "weapon"

    def test_knave_melee_compendium_entries_are_dict(self, knave: System) -> None:
        entries = knave.compendiums["melee"].entries
        assert isinstance(entries, dict)
        assert "dagger" in entries

    def test_wyrdbound_loads_all_compendiums(self, wyrdbound: System) -> None:
        # 5 compendium YAML files in systems/wyrdbound-quickstart-1e/compendiums/
        assert len(wyrdbound.compendiums) == 5

    def test_wyrdbound_weapons_compendium_entries_keyed_by_id(
        self, wyrdbound: System
    ) -> None:
        # wyrdbound compendiums use list-with-id entries; loader converts to dict
        entries = wyrdbound.compendiums["weapons"].entries
        assert isinstance(entries, dict)
        assert "dagger" in entries


# ---------------------------------------------------------------------------
# Flows
# ---------------------------------------------------------------------------


class TestSystemLoaderFlows:
    def test_knave_loads_all_flows(self, knave: System) -> None:
        # 14 flow YAML files in systems/knave_1e/flows/ (recursive)
        assert len(knave.flows) == 14

    def test_knave_has_character_creation_flow(self, knave: System) -> None:
        assert "character_creation" in knave.flows

    def test_knave_character_creation_flow_has_steps(self, knave: System) -> None:
        assert len(knave.flows["character_creation"].steps) > 0

    def test_wyrdbound_loads_all_flows(self, wyrdbound: System) -> None:
        # 6 flow YAML files in systems/wyrdbound-quickstart-1e/flows/ (recursive)
        assert len(wyrdbound.flows) == 6

    def test_wyrdbound_has_character_creation_flow(self, wyrdbound: System) -> None:
        assert "character_creation" in wyrdbound.flows


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


class TestSystemLoaderPrompts:
    def test_knave_loads_all_prompts(self, knave: System) -> None:
        # 5 prompt YAML files in systems/knave_1e/prompts/
        assert len(knave.prompts) == 5

    def test_knave_has_fix_json_prompt(self, knave: System) -> None:
        assert "fix_json" in knave.prompts

    def test_knave_fix_json_prompt_has_template(self, knave: System) -> None:
        assert knave.prompts["fix_json"].prompt_template

    def test_wyrdbound_loads_all_prompts(self, wyrdbound: System) -> None:
        # 1 prompt YAML file in systems/wyrdbound-quickstart-1e/prompts/
        assert len(wyrdbound.prompts) == 1


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------


class TestSystemLoaderSources:
    def test_knave_loads_all_sources(self, knave: System) -> None:
        # 1 source YAML file in systems/knave_1e/sources/
        assert len(knave.sources) == 1

    def test_knave_has_toolkit_source(self, knave: System) -> None:
        assert "toolkit" in knave.sources

    def test_wyrdbound_has_core_rules_source(self, wyrdbound: System) -> None:
        assert "core_rules" in wyrdbound.sources


# ---------------------------------------------------------------------------
# Currency
# ---------------------------------------------------------------------------


class TestSystemLoaderCurrency:
    def test_knave_has_currency(self, knave: System) -> None:
        assert knave.currency is not None

    def test_wyrdbound_has_currency(self, wyrdbound: System) -> None:
        assert wyrdbound.currency is not None

    def test_wyrdbound_currency_base_unit(self, wyrdbound: System) -> None:
        assert wyrdbound.currency is not None
        assert wyrdbound.currency.base_unit == "gold"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestSystemValidation:
    def test_knave_validates_with_no_errors(self, knave: System) -> None:
        errors = knave.validate()
        assert errors == [], f"Unexpected errors: {errors}"

    def test_wyrdbound_validates_with_no_errors(self, wyrdbound: System) -> None:
        errors = wyrdbound.validate()
        assert errors == [], f"Unexpected errors: {errors}"
