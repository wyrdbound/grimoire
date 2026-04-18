"""Examples demonstrating SystemLoader usage.

Shows how to load a GRIMOIRE system directory into a System object,
inspect its contents, and run validation.
"""

from pathlib import Path

from grimoire.loader import SystemLoader, SystemLoadError

SYSTEMS_DIR = Path(__file__).parent.parent / "systems"


def example_load_and_validate(system_name: str) -> None:
    """Load a system directory and run validation, printing any errors."""
    loader = SystemLoader()
    system_path = SYSTEMS_DIR / system_name

    print(f"\n── Loading system: {system_path} ──")
    system = loader.load(system_path)

    print(f"  id:          {system.id}")
    print(f"  name:        {system.name}")
    print(f"  version:     {system.version}")
    print(f"  models:      {len(system.models)}")
    print(f"  flows:       {len(system.flows)}")
    print(f"  tables:      {len(system.tables)}")
    print(f"  compendiums: {len(system.compendiums)}")
    print(f"  prompts:     {len(system.prompts)}")
    print(f"  sources:     {len(system.sources)}")

    errors = system.validate()
    if errors:
        print(f"\n  ✗ Validation errors ({len(errors)}):")
        for error in errors:
            print(f"    - {error}")
    else:
        print("\n  ✓ System is valid")


def example_inspect_models(system_name: str = "knave-1e") -> None:
    """Load a system and print the names of all loaded models."""
    loader = SystemLoader()
    system = loader.load(SYSTEMS_DIR / system_name)

    print(f"\n── Models in '{system.name}' ──")
    for model_id, model in sorted(system.models.items()):
        extends = f"  extends: {model.extends}" if model.extends else ""
        print(f"  {model_id}: {model.name}{extends}")


def example_inspect_flows(system_name: str = "knave-1e") -> None:
    """Load a system and print a summary of all loaded flows."""
    loader = SystemLoader()
    system = loader.load(SYSTEMS_DIR / system_name)

    print(f"\n── Flows in '{system.name}' ──")
    for flow_id, flow in sorted(system.flows.items()):
        step_count = len(flow.steps)
        print(f"  {flow_id}: {flow.name} ({step_count} steps)")


def example_inspect_compendiums(system_name: str = "knave-1e") -> None:
    """Load a system and print compendium entry counts."""
    loader = SystemLoader()
    system = loader.load(SYSTEMS_DIR / system_name)

    print(f"\n── Compendiums in '{system.name}' ──")
    for comp_id, comp in sorted(system.compendiums.items()):
        print(
            f"  {comp_id}: {comp.name}  "
            f"(model={comp.model}, entries={len(comp.entries)})"
        )


def example_error_handling() -> None:
    """Demonstrate error handling for invalid system paths."""
    loader = SystemLoader()

    print("\n── Error handling examples ──")

    # Non-existent path
    try:
        loader.load(Path("/nonexistent/system"))
    except SystemLoadError as e:
        print(f"  Non-existent path → SystemLoadError: {e}")

    # Directory missing system.yaml
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            loader.load(Path(tmpdir))
        except SystemLoadError as e:
            print(f"  Missing system.yaml → SystemLoadError: {e}")


if __name__ == "__main__":
    # Run all examples
    for system_dir in ["knave-1e", "wyrdbound-quickstart-1e"]:
        example_load_and_validate(system_dir)

    example_inspect_models("knave-1e")
    example_inspect_flows("knave-1e")
    example_inspect_compendiums("knave-1e")
    example_error_handling()
