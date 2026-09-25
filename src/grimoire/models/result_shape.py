"""Check at load that flows read table results in the shape the table gives.

spec/table_spec.md "Multiple Entries": an ordinary table's result is
`result.entry`; a `multiple_entries: true` table's is `result.entries`. The
other name is undefined, so a mismatch would otherwise fail on the first roll.
This module finds every mismatch the loader can see, which is every step that
names its table directly and — by treating each `{{ … }}` in a table name as a
wildcard over table ids — every step whose table name is templated.
"""

import re
from collections.abc import Iterator
from typing import Any

import jinja2
from jinja2 import nodes

from .flow import FlowDefinition, StepType
from .table import TableDefinition

_ENV = jinja2.Environment()
_TEMPLATE = re.compile(r"\{\{.*?\}\}")
_RESULT_FIELDS = {"entry", "entries"}


def result_fields(template: str) -> set[str]:
    """Return which of `result.entry` / `result.entries` a template reads.

    Parses the template with Jinja2, so `result.entry` and `result['entry']`
    are both found and text that merely looks like them is not.

    Raises:
        jinja2.TemplateSyntaxError: The template does not parse.
    """
    found: set[str] = set()
    tree = _ENV.parse(template)
    for node in tree.find_all((nodes.Getattr, nodes.Getitem)):
        assert isinstance(node, (nodes.Getattr, nodes.Getitem))
        target = node.node
        if not (isinstance(target, nodes.Name) and target.name == "result"):
            continue
        if isinstance(node, nodes.Getattr):
            name: Any = node.attr
        elif isinstance(node, nodes.Getitem) and isinstance(node.arg, nodes.Const):
            name = node.arg.value
        else:
            continue
        if name in _RESULT_FIELDS:
            found.add(name)
    return found


def candidate_tables(
    reference: str, tables: dict[str, TableDefinition]
) -> list[TableDefinition]:
    """Tables a (possibly templated) table reference could name at runtime."""
    if "{{" not in reference and "{%" not in reference:
        table = tables.get(reference)
        return [table] if table is not None else []
    pieces = _TEMPLATE.split(reference)
    pattern = re.compile(".+".join(re.escape(piece) for piece in pieces))
    return [t for tid, t in tables.items() if pattern.fullmatch(tid)]


def _strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def check_flow(flow_id: str, flow: FlowDefinition, tables: dict[str, Any]) -> list[str]:
    """Return every table-result shape error in one flow."""
    errors: list[str] = []
    for step in flow.steps:
        where = f"Flow '{flow_id}' step '{step.id}'"
        if step.type == StepType.TABLE_ROLL:
            for roll in step.tables:
                errors.extend(_check_roll(where, roll.table, roll.actions, tables))
        elif step.type == StepType.TABLE_SEQUENCE and step.table_sequence:
            seq = step.table_sequence
            errors.extend(_check_roll(where, seq.table, seq.actions, tables))
            errors.extend(_check_no_result(where, step.actions))
        elif step.type == StepType.PLAYER_CHOICE and isinstance(
            step.choice_source, dict
        ):
            reference = step.choice_source.get("table")
            if isinstance(reference, str):
                errors.extend(_check_choice(where, reference, tables))
    return errors


def _check_roll(
    where: str, reference: str, actions: Any, tables: dict[str, Any]
) -> list[str]:
    candidates = candidate_tables(reference, tables)
    if not candidates:
        return [f"{where}: no table matches {reference!r}"]
    fields: set[str] = set()
    for text in _strings(actions):
        if "{{" not in text and "{%" not in text:
            continue
        try:
            fields |= result_fields(text)
        except jinja2.TemplateSyntaxError as exc:
            return [f"{where}: template {text!r} does not parse: {exc.message}"]
    errors = []
    for table in candidates:
        if table.multiple_entries and "entry" in fields:
            errors.append(
                f"{where}: table '{table.id}' declares `multiple_entries: true`, "
                "so its result is `result.entries`, not `result.entry`"
            )
        if not table.multiple_entries and "entries" in fields:
            errors.append(
                f"{where}: table '{table.id}' yields one entry per roll, so its "
                "result is `result.entry`, not `result.entries`"
            )
    return errors


def _check_no_result(where: str, actions: Any) -> list[str]:
    """`result` is per roll; a table_sequence's step-level actions cannot read it."""
    for text in _strings(actions):
        if "{{" not in text and "{%" not in text:
            continue
        try:
            tree = _ENV.parse(text)
        except jinja2.TemplateSyntaxError as exc:
            return [f"{where}: template {text!r} does not parse: {exc.message}"]
        if any(n.name == "result" for n in tree.find_all(nodes.Name)):
            return [
                f"{where}: `result` is only available in the sequence's own "
                "actions, which run once per roll; the step's actions run once, "
                "after every roll"
            ]
    return []


def _check_choice(where: str, reference: str, tables: dict[str, Any]) -> list[str]:
    candidates = candidate_tables(reference, tables)
    if not candidates:
        return [f"{where}: no table matches {reference!r}"]
    return [
        f"{where}: table '{table.id}' declares `multiple_entries: true` and "
        "cannot be the source of a player_choice"
        for table in candidates
        if table.multiple_entries
    ]
