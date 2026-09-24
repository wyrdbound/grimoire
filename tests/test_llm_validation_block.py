"""The `llm_generation` `validation` block (spec/flow_spec.md)."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from grimoire.loader import SystemLoader, SystemLoadError

KNAVE_DIR = Path(__file__).parent.parent / "systems" / "knave-1e"


def _load(tmp_path: Path, validation: dict[str, Any]) -> Any:
    (tmp_path / "flows").mkdir()
    (tmp_path / "system.yaml").write_text(
        yaml.safe_dump({"id": "t", "kind": "system", "name": "T"})
    )
    flow = {
        "id": "f",
        "kind": "flow",
        "name": "F",
        "steps": [
            {
                "id": "ask",
                "type": "llm_generation",
                "prompt_id": "p",
                "validation": validation,
            }
        ],
    }
    (tmp_path / "flows" / "f.yaml").write_text(yaml.safe_dump(flow))
    return SystemLoader().load(tmp_path).flows["f"].steps[0].validation


SCHEMA = {"type": "object"}


def test_defaults(tmp_path: Path) -> None:
    v = _load(tmp_path, {"type": "json"})
    assert (v.max_attempts, v.cleanup_enabled, v.on_failure) == (3, True, "continue")


def test_fallback_value_may_be_null(tmp_path: Path) -> None:
    v = _load(
        tmp_path,
        {"type": "json", "on_failure": "fallback", "fallback_value": None},
    )
    assert v.on_failure == "fallback" and v.fallback_value is None


@pytest.mark.parametrize(
    ("validation", "message"),
    [
        ({"type": "xml"}, "`type` must be"),
        ({"type": "json_schema"}, "requires a `schema`"),
        ({"type": "json", "max_attempts": 0}, "`max_attempts` must be"),
        ({"type": "json", "max_attempts": True}, "`max_attempts` must be"),
        ({"type": "json", "on_failure": "retry"}, "`on_failure` must be"),
        ({"type": "json", "on_failure": "fallback"}, "requires a `fallback_value`"),
        ({"type": "json_schema", "schema": SCHEMA, "on_failure": "ignore"}, "must"),
    ],
)
def test_invalid_blocks_are_rejected(
    tmp_path: Path, validation: dict[str, Any], message: str
) -> None:
    with pytest.raises(SystemLoadError, match=message):
        _load(tmp_path, validation)


def test_knave_saving_throw_blocks_load() -> None:
    flow = SystemLoader().load(KNAVE_DIR).flows["perform_saving_throw"]
    blocks = [s.validation for s in flow.steps if s.validation is not None]
    assert len(blocks) == 2
    assert all(b.type == "json_schema" and b.schema for b in blocks)
