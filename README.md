# GRIMOIRE

**GRIMOIRE** (Generic Rule Implementation Model for Omniversal Interactive Roleplaying Engines) is a Python library for loading, validating, and working with structured tabletop RPG system definitions.

It provides a declarative YAML-based specification format for encoding game systems — covering models, flows, tables, compendiums, prompts, and sources — and a Python loader that parses and validates those definitions into typed Python objects.

GRIMOIRE is system-agnostic and not tied to any particular game or application. It is designed to be used as a foundation for tools that need to reason about RPG rules programmatically: AI game masters, character generators, rule validators, or any application that needs to load and execute structured game logic.

---

## Installation

To add to a uv-managed project:

```bash
uv add grimoire-spec
```

Or to install directly into an environment:

```bash
uv pip install grimoire-spec
```

## Quick Start

```python
from pathlib import Path
from grimoire.loader import SystemLoader

loader = SystemLoader()
system = loader.load(Path("systems/knave-1e"))

print(system.name)          # "Knave (1st Edition)"
print(len(system.models))   # number of loaded models
print(len(system.flows))    # number of loaded flows

errors = system.validate()
if not errors:
    print("System is valid")
```

See the [`examples/`](examples/) directory for more usage patterns.

## System Definition Format

A GRIMOIRE system is a directory containing YAML files organised by type:

```
my-system/
  system.yaml          # root metadata, currency, attribution
  models/              # data model definitions
  flows/               # rule sequences and game mechanics
  tables/              # random tables
  compendiums/         # item/entity catalogues
  prompts/             # AI prompt templates
  sources/             # source material attribution
```

Full specification for each file type is in [`spec/`](spec/).

## Development

This project uses [`uv`](https://github.com/astral-sh/uv) for environment and dependency management.

### Setup

```bash
uv sync --extra dev
```

### Run tests

```bash
uv run pytest
```

### Linting and formatting

```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

### Type checking

```bash
uv run mypy src/
```

### Run an example

```bash
uv run python examples/load_system.py
```

## Project Structure

```
src/grimoire/       # library source
  loader.py         # SystemLoader — entry point for loading a system directory
  models/           # typed Python models for each definition type
spec/               # YAML format specification documents
systems/            # bundled example systems (knave-1e, wyrdbound-quickstart-1e)
examples/           # usage examples
tests/              # test suite
```

## Contributing

Contributions are welcome. Please follow the existing code style (enforced by Ruff) and ensure all tests pass before submitting a pull request. New features should be accompanied by tests and an example in `examples/`.

## License

See [LICENSE](LICENSE) for details.
