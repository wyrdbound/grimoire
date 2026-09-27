"""Attribute names beginning with `_` are reserved (spec/model_spec.md).

The prefix is reserved for data GRIMOIRE itself records on an instance. The
first such key is `_model`: an instance of a model that extends another model
records its own model id there, so a `weapon` stored in an `of: item` list is
still a weapon after it has been saved as plain data and read back. A model
that declared its own `_model` attribute would collide with that tag, so a
reserved name is a definition error, reported when the system is validated.
"""

from pathlib import Path
from typing import Any

import pytest

from grimoire.loader import SystemLoader
from grimoire.models.model_definition import ModelDefinition

SYSTEMS = Path(__file__).parent.parent / "systems"


def _model(attributes: dict[str, Any]) -> ModelDefinition:
    return ModelDefinition(id="thing", name="Thing", attributes=attributes)


class TestReservedPrefix:
    def test_the_model_tag_cannot_be_declared(self) -> None:
        errors = _model({"_model": {"type": "str"}}).validate()
        assert len(errors) == 1
        assert "'_model'" in errors[0]
        assert "reserved" in errors[0]

    def test_any_leading_underscore_is_reserved(self) -> None:
        errors = _model({"_secret": {"type": "int"}}).validate()
        assert len(errors) == 1
        assert "'_secret'" in errors[0]

    def test_a_leaf_inside_a_group_is_checked(self) -> None:
        attrs = {"stats": {"_hidden": {"type": "int"}, "score": {"type": "int"}}}
        errors = _model(attrs).validate()
        assert len(errors) == 1
        assert "'stats._hidden'" in errors[0]

    def test_a_group_name_is_checked(self) -> None:
        attrs = {"_meta": {"note": {"type": "str"}}}
        errors = _model(attrs).validate()
        assert len(errors) == 1
        assert "'_meta'" in errors[0]

    @pytest.mark.parametrize("name", ["model", "type", "kind", "name_", "a_b"])
    def test_ordinary_names_are_allowed(self, name: str) -> None:
        assert _model({name: {"type": "str"}}).validate() == []


class TestInstanceTag:
    def test_an_instance_may_carry_the_model_tag(self) -> None:
        model = _model({"name": {"type": "str"}})
        assert model.validate_instance({"_model": "thing", "name": "Rope"}) == []


class TestReferenceSystems:
    @pytest.mark.parametrize("system_id", ["knave-1e", "wyrdbound-quickstart-1e"])
    def test_no_reference_model_uses_the_reserved_prefix(self, system_id: str) -> None:
        system = SystemLoader().load(SYSTEMS / system_id)
        assert [e for e in system.validate() if "reserved" in e] == []
