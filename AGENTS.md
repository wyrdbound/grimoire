# Developer Guide & AI Guidance

This document is the authoritative governance and quick-reference guide for
working on the GRIMOIRE repository. It binds all code, review, and planning.
Where a section uses MUST / MUST NOT, compliance is not optional; SHOULD
carries a stated rationale and requires justification to deviate.

This repository holds three things: the **GRIMOIRE specification** (`spec/`),
a **loader library** that parses and validates systems against it
(`src/grimoire/`), and **reference systems** that exercise both
(`systems/`). Most of the guidance below exists to keep those three in
agreement, because when they drift it is rarely obvious which one is wrong.

## AI Guidance

Always remember the following points as you are working on this code base:

1. **Use `uv`** to create the Python virtual env, manage dependencies, and run
   scripts. No bare `pip`, `python`, or manual venv activation.
2. **NEVER mask issues with fallbacks that hide errors.** Prefer explicit
   errors. Fixing issues is the only way to ensure a stable system.
3. **Follow good software development practices** (like SOLID).
4. **Simpler is better.**
5. **Provide functionality in a clear and maintainable manner.** Avoid
   special-cases or hack fixes simply to get around issues.
6. **Do NOT make bandaid fixes** that break the rearchitecture goals for the
   library. Always respect the architectural boundaries.
7. **Practice Test-Driven Development (TDD)** — red, green, refactor:
   - **Red:** write a failing test that defines the desired behaviour
   - **Green:** write minimal code to make it pass
   - **Refactor:** improve quality while keeping tests green

   This forces clear requirement thinking before coding, ensures everything is
   testable, creates a safety net for refactoring, documents expected
   behaviour, and prevents scope creep.
8. **All imports at the top of the file**, following standard Python
   conventions. Avoid dynamic imports or imports inside functions. If circular
   dependencies arise, that is a sign the structure needs reconsidering.
9. **New features get an example** in `examples/`, following the existing
   patterns: clear docstring, multiple use cases, well-commented code.
10. **The specification is not written in stone — but you do not change it.**
    See "Changing the specification" below. Question it freely; propose
    revisions; never edit `spec/` without Justin's explicit confirmation.

## Repository Structure

| Path | What it is |
| --- | --- |
| `spec/` | The GRIMOIRE specification. The contract. |
| `src/grimoire/` | `SystemLoader` and the typed definitions it produces |
| `systems/` | Reference systems (`knave-1e`, `wyrdbound-quickstart-1e`) |
| `examples/` | Runnable usage examples |
| `tests/` | The test suite |

The loader parses and validates; it does not execute. Flow execution,
adjudication and anything resembling a game engine live downstream, in
Wyrdbound. A change that starts to look like an interpreter belongs there.

## Core Principles

### I. The specification is the contract, and it can be wrong

`spec/` is what system authors write against and what implementers build to.
It is also ours, and it has had real bugs: syntaxes that no implementation
supported, two spellings of the same feature in one document, examples that
could not execute as written.

So: treat the spec as authoritative for *what a system file means*, and treat
disagreement between the spec, the loader, and the shipped systems as a
question to be settled empirically — not as proof the spec is right.

**A documented syntax that no implementation supports and no system uses is
evidence about the spec, not about the implementations.**

### II. Changing the specification

A spec change MUST be confirmed by Justin before it is made. This is not
bureaucracy: system definitions are written by other people against the
document, so a unilateral change silently invalidates their content.

When you find a defect:

1. Establish what is actually true by running the code, not by reading.
2. Write the finding down — what the spec says, what the implementation does,
   what the shipped systems do.
3. Propose the change and wait for confirmation.
4. If it is approved, change the spec, the affected reference systems and the
   loader in the same slice, so the three never disagree in a released state.

### III. Hand-authorability is the success metric

GRIMOIRE's premise is that a competent GM can write a system by hand. The
measure of a proposed primitive is not how many games it covers but whether
the format stays writable by a person in an afternoon.

Coverage arguments are seductive and one-sided. "N of M systems have this
mechanic" is an argument that the mechanic exists, not that a given set of
primitives is the right way to express it. Every addition MUST be justified
against a simpler rejected alternative.

### IV. Expression syntax is bare names

Derived expressions, `range` expressions and `validations` expressions are
evaluated against the model instance. Attributes are referenced by **bare
name**, with root-relative dotted paths for nested attributes, inside
`{{ }}`. There is no instance prefix: not `this.`, not `$`.

Jinja2 globals are not available in the evaluation environment, so an
attribute may safely be named `range` or `dict` and a misspelled name always
raises. See `spec/model_spec.md` § Expression Evaluation Context.

### V. Reference systems are tests, not samples

`knave-1e` and `wyrdbound-quickstart-1e` are how the spec gets exercised. A
spec feature that no reference system uses is untested, and a reference system
that cannot load is a broken build. When the spec changes, they change with
it.

## Engineering Standards

- **`uv` for dependency management.** `uv sync --extra dev`, `uv run …`.
  `uv.lock` MUST be committed.
- **Explicit errors over fallbacks.** Silent failures are prohibited. A loader
  that accepts a malformed system produces a broken game later, further from
  the cause.
- **Imports at the top.** PEP 8, always.
- **Type hints on all public APIs.** `mypy` MUST pass.
- **Docstrings on all public modules, classes and functions.**
- **Backward compatibility.** Existing system definitions MUST continue to
  load. New spec features are opt-in; absent fields behave as before.
- **Tests first.** See AI Guidance §7.

## Quality Checks

```bash
uv run ruff format .
uv run ruff check .
uv run mypy src/
uv run pytest -q
```

Run them iteratively until clean, before every commit.

## Governance

`AGENTS.md` is binding on all work in this repository.

The specification in `spec/` is authoritative for system definition formats
and is changed only with Justin's explicit confirmation (Principle II).
