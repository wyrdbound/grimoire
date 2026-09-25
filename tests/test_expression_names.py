"""Every name a model expression reads is one of that model's root attributes.

Paths in derived, range and validation expressions are root-relative
(spec/model_spec.md, "Expression Evaluation Context"). Knave's
`armor.defense` was derived as `{{ 10 + bonus }}`; `bonus` is not a root
attribute, so the character model could not be instantiated at all.
"""

from pathlib import Path
from typing import Any

import pytest
from jinja2 import Environment, meta

from grimoire.loader import SystemLoader

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"
_ENV = Environment()


def _expressions(attrs: dict[str, Any], prefix: str = ""):
    for key, value in attrs.items():
        if not isinstance(value, dict):
            continue
        path = f"{prefix}{key}"
        if "type" in value:
            for field in ("derived", "range"):
                text = value.get(field)
                if isinstance(text, str) and "{{" in text:
                    yield path, field, text
        else:
            yield from _expressions(value, f"{path}.")


@pytest.mark.parametrize("system", ["knave-1e", "wyrdbound-quickstart-1e"])
def test_expression_names_are_root_attributes(system: str) -> None:
    loaded = SystemLoader().load(SYSTEMS_DIR / system)
    problems = []
    for model in loaded.models.values():
        roots = set(model.attributes)
        pending = list(model.extends)
        while pending:
            parent = loaded.models[pending.pop()]
            roots |= set(parent.attributes)
            pending.extend(parent.extends)
        found = list(_expressions(model.attributes))
        found += [
            ("validations", "expression", v.expression) for v in model.validations
        ]
        for path, field, text in found:
            names = meta.find_undeclared_variables(_ENV.parse(text))
            for name in sorted(names - roots):
                problems.append(f"{model.id}.{path} {field} {text!r}: {name!r}")
    assert problems == []
