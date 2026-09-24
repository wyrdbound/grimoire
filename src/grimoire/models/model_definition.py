"""Model definition models for GRIMOIRE runner."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AttributeDefinition:
    """Model attribute definition."""

    type: str  # int, str, float, bool, or model ID
    default: Any | None = None
    range: str | None = None  # e.g., "1..20", "1..", etc.
    enum: list[str] | None = None
    derived: str | None = None  # Formula for derived attributes
    description: str | None = None
    of: str | None = None  # Element type for list/map attributes
    # The only presence flag. Attributes are required unless marked optional.
    optional: bool = False


def attribute_definition_errors(path: str, data: dict[str, Any]) -> list[str]:
    """Return the spec violations in one raw attribute definition.

    Checked on the raw mapping, because only the mapping can tell an explicit
    ``default: null`` apart from an omitted default.
    """
    errors = []
    if "required" in data:
        errors.append(
            f"Attribute '{path}': `required` is not an attribute field. "
            "Attributes are required by default; mark an attribute that may be "
            "left without a value `optional: true`."
        )
    if "default" in data and data["default"] is None:
        errors.append(
            f"Attribute '{path}': `default: null` is not a valid default. An "
            "attribute that may be left without a value should be marked "
            "`optional: true` and given no default."
        )
    if data.get("optional") and data.get("default") is not None:
        errors.append(
            f"Attribute '{path}': an optional attribute cannot have a default. "
            "Set its starting value when the instance is created instead."
        )
    return errors


def _to_attribute_definition(data: dict[str, Any]) -> AttributeDefinition:
    """Build an AttributeDefinition from a raw mapping.

    ``required`` is dropped here so that a definition still using it is
    reported by ``ModelDefinition.validate`` rather than crashing the build.
    """
    return AttributeDefinition(
        **{key: value for key, value in data.items() if key != "required"}
    )


@dataclass
class ValidationRule:
    """Model validation rule."""

    expression: str
    message: str


@dataclass
class ModelDefinition:
    """Complete model definition."""

    id: str
    name: str
    kind: str = "model"
    description: str | None = None
    version: int = 1

    extends: list[str] = field(default_factory=list)
    attributes: dict[str, AttributeDefinition | dict[str, Any]] = field(
        default_factory=dict
    )
    validations: list[ValidationRule] = field(default_factory=list)

    def get_attribute(self, attr_path: str) -> AttributeDefinition | None:
        """Get an attribute definition by path (supports nested attributes)."""
        parts = attr_path.split(".")
        current = self.attributes

        for part in parts[:-1]:
            if part not in current:
                return None
            attr = current[part]
            if isinstance(attr, AttributeDefinition):
                return None  # Can't traverse further
            current = attr

        final_part = parts[-1]
        if final_part not in current:
            return None

        attr = current[final_part]
        if isinstance(attr, AttributeDefinition):
            return attr
        elif isinstance(attr, dict) and "type" in attr:
            # Convert dict to AttributeDefinition
            return _to_attribute_definition(attr)

        return None

    def get_all_attributes(self) -> dict[str, AttributeDefinition]:
        """Get all attributes, optionally including inherited ones."""
        # TODO: Implement inheritance resolution
        all_attrs = {}

        def _extract_attributes(attrs: dict[str, Any], prefix: str = "") -> None:
            for key, value in attrs.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, AttributeDefinition):
                    all_attrs[full_key] = value
                elif isinstance(value, dict):
                    if "type" in value:
                        # Convert dict to AttributeDefinition
                        all_attrs[full_key] = _to_attribute_definition(value)
                    else:
                        # Nested attributes
                        _extract_attributes(value, full_key)

        _extract_attributes(self.attributes)
        return all_attrs

    def validate_instance(self, instance: dict[str, Any]) -> list[str]:
        """Validate an instance against this model."""
        errors = []
        all_attrs = self.get_all_attributes()

        # Check required attributes. Derived attributes are computed, and an
        # absent attribute with a default receives it when the instance is
        # created, so neither has to be present in the data.
        for attr_path, attr_def in all_attrs.items():
            if attr_def.optional or attr_def.derived is not None:
                continue
            if not self._has_nested_value(instance, attr_path):
                if attr_def.default is None:
                    errors.append(f"Required attribute '{attr_path}' is missing")
            elif self._get_nested_value(instance, attr_path) is None:
                errors.append(f"Required attribute '{attr_path}' cannot be null")

        # Validate attribute values
        for attr_path, attr_def in all_attrs.items():
            if self._has_nested_value(instance, attr_path):
                value = self._get_nested_value(instance, attr_path)
                if value is not None:
                    attr_errors = self._validate_attribute_value(
                        attr_path, value, attr_def
                    )
                    errors.extend(attr_errors)

        # Run validation rules
        # TODO: Implement expression evaluation

        return errors

    def _has_nested_value(self, obj: dict[str, Any], path: str) -> bool:
        """Check if a nested value exists."""
        try:
            self._get_nested_value(obj, path)
            return True
        except (KeyError, TypeError):
            return False

    def _get_nested_value(self, obj: dict[str, Any], path: str) -> Any:
        """Get a nested value by dot-separated path."""
        parts = path.split(".")
        current = obj

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise KeyError(f"Path '{path}' not found")

        return current

    def _validate_attribute_value(
        self, attr_path: str, value: Any, attr_def: AttributeDefinition
    ) -> list[str]:
        """Validate a single attribute value."""
        errors = []

        # Type validation
        expected_type = attr_def.type
        if expected_type == "int" and not isinstance(value, int):
            errors.append(f"Attribute '{attr_path}' must be an integer")
        elif expected_type == "str" and not isinstance(value, str):
            errors.append(f"Attribute '{attr_path}' must be a string")
        elif expected_type == "float" and not isinstance(value, int | float):
            errors.append(f"Attribute '{attr_path}' must be a number")
        elif expected_type == "bool" and not isinstance(value, bool):
            errors.append(f"Attribute '{attr_path}' must be a boolean")

        # Range validation
        if attr_def.range and isinstance(value, int | float):
            range_errors = self._validate_range(attr_path, value, attr_def.range)
            errors.extend(range_errors)

        # Enum validation
        if attr_def.enum and value not in attr_def.enum:
            errors.append(
                f"Attribute '{attr_path}' must be one of: {', '.join(attr_def.enum)}"
            )

        return errors

    def _validate_range(
        self, attr_path: str, value: int | float, range_spec: str
    ) -> list[str]:
        """Validate that a value falls within the specified range."""
        errors = []

        try:
            # Parse range specification (e.g., "1..20", "1..", "..20")
            if ".." in range_spec:
                parts = range_spec.split("..")
                min_val = int(parts[0]) if parts[0] else None
                max_val = int(parts[1]) if parts[1] else None

                if min_val is not None and value < min_val:
                    errors.append(f"Attribute '{attr_path}' must be >= {min_val}")
                if max_val is not None and value > max_val:
                    errors.append(f"Attribute '{attr_path}' must be <= {max_val}")
            else:
                # Exact value
                expected = int(range_spec)
                if value != expected:
                    errors.append(f"Attribute '{attr_path}' must equal {expected}")
        except ValueError:
            errors.append(
                f"Invalid range specification '{range_spec}' "
                f"for attribute '{attr_path}'"
            )

        return errors

    def validate(self) -> list[str]:
        """Validate the model definition and return any errors."""
        errors = []

        # Validate required fields
        if not self.id:
            errors.append("Model ID is required")
        if not self.name:
            errors.append("Model name is required")
        if self.kind != "model":
            errors.append(f"Model kind must be 'model', got '{self.kind}'")

        # TODO: Validate extends references
        errors.extend(self._attribute_definition_errors(self.attributes))
        # TODO: Validate validation expressions

        return errors

    def _attribute_definition_errors(
        self, attrs: dict[str, Any], prefix: str = ""
    ) -> list[str]:
        """Check every raw attribute definition, recursing into groups."""
        errors = []
        for key, value in attrs.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                if "type" in value:
                    errors.extend(attribute_definition_errors(path, value))
                else:
                    errors.extend(self._attribute_definition_errors(value, path))
        return errors
