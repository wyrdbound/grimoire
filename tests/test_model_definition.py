"""Tests for ModelDefinition presence, default and null rules (spec/model_spec.md)."""

from pathlib import Path
from typing import Any

from grimoire.loader import SystemLoader
from grimoire.models.model_definition import AttributeDefinition, ModelDefinition


def _model(attributes: dict[str, Any]) -> ModelDefinition:
    return ModelDefinition(id="thing", name="Thing", attributes=attributes)


class TestPresenceFlag:
    def test_attributes_are_required_by_default(self) -> None:
        assert AttributeDefinition(type="int").optional is False

    def test_required_field_is_gone(self) -> None:
        assert not hasattr(AttributeDefinition(type="int"), "required")

    def test_required_key_is_reported(self) -> None:
        errors = _model({"hp": {"type": "int", "required": False}}).validate()
        assert len(errors) == 1
        assert "`required` is not an attribute field" in errors[0]

    def test_required_key_does_not_crash_instance_validation(self) -> None:
        model = _model({"hp": {"type": "int", "required": True}})
        assert model.validate_instance({"hp": 3}) == []


class TestDefaultRule:
    def test_default_on_required_attribute_is_valid(self) -> None:
        assert _model({"level": {"type": "int", "default": 1}}).validate() == []

    def test_explicit_null_default_is_rejected(self) -> None:
        errors = _model({"level": {"type": "int", "default": None}}).validate()
        assert len(errors) == 1
        assert "`default: null` is not a valid default" in errors[0]

    def test_default_on_optional_attribute_is_rejected(self) -> None:
        attrs = {"cloak": {"type": "str", "optional": True, "default": "cloak"}}
        errors = _model(attrs).validate()
        assert len(errors) == 1
        assert "optional attribute cannot have a default" in errors[0]

    def test_rules_apply_inside_groups(self) -> None:
        attrs = {
            "equipped": {
                "covering": {"type": "str", "optional": True, "default": "cloak"}
            }
        }
        errors = _model(attrs).validate()
        assert len(errors) == 1
        assert "'equipped.covering'" in errors[0]


class TestInstancePresence:
    def test_missing_required_attribute_is_an_error(self) -> None:
        errors = _model({"hp": {"type": "int"}}).validate_instance({})
        assert errors == ["Required attribute 'hp' is missing"]

    def test_null_required_attribute_is_an_error(self) -> None:
        errors = _model({"hp": {"type": "int"}}).validate_instance({"hp": None})
        assert errors == ["Required attribute 'hp' cannot be null"]

    def test_absent_optional_attribute_is_valid(self) -> None:
        model = _model({"note": {"type": "str", "optional": True}})
        assert model.validate_instance({}) == []

    def test_null_optional_attribute_is_valid(self) -> None:
        model = _model({"note": {"type": "str", "optional": True}})
        assert model.validate_instance({"note": None}) == []

    def test_absent_attribute_with_default_is_valid(self) -> None:
        model = _model({"level": {"type": "int", "default": 1}})
        assert model.validate_instance({}) == []

    def test_absent_derived_attribute_is_valid(self) -> None:
        attrs = {
            "hp": {"type": "int"},
            "half": {"type": "int", "derived": "{{ hp // 2 }}"},
        }
        assert _model(attrs).validate_instance({"hp": 4}) == []


class TestSystemValidationIncludesModels:
    def test_system_validate_reports_model_errors(self) -> None:
        system_dir = (
            Path(__file__).parent.parent / "systems" / "wyrdbound-quickstart-1e"
        )
        system = SystemLoader().load(system_dir)
        system.models["character"].attributes["name"] = {"type": "str", "default": None}
        errors = [e for e in system.validate() if e.startswith("Model ")]
        assert len(errors) == 1
        assert errors[0].startswith("Model 'character': Attribute 'name'")
