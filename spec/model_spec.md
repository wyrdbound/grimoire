# GRIMOIRE Model Definition Specification

## Overview

Model Definition files define the data structures for game entities in GRIMOIRE systems. Models describe the attributes, validations, and relationships that define characters, items, weapons, armor, and other game objects. They serve as templates that can be instantiated during gameplay.

Models support inheritance through the `extends` field, allowing specialized models to build upon base models while adding their own unique attributes.

## File Structure

All model definition files must follow this top-level structure:

```yaml
id: unique_model_identifier
kind: model
name: "Human Readable Model Name"
description: "Description of what this model represents"
version: 1
extends: [] # optional
attributes: {}
validations: [] # optional
```

### Top-Level Fields

- **`id`** (required): Unique identifier for the model within the system
- **`kind`** (required): Must be `"model"` to indicate this file defines a model
- **`name`** (required): Human-readable name for the model
- **`description`** (optional): Detailed description of what the model represents
- **`version`** (optional): Version number for the model definition
- **`extends`** (optional): Array of model IDs that this model inherits from
- **`attributes`** (required): Map of attribute definitions that define the model's structure
- **`validations`** (optional): Array of validation rules that instances must satisfy

## Attributes

Attributes define the properties that instances of this model will have. Each attribute specifies its type, constraints, and behavior:

```yaml
attributes:
  name:
    type: str
    default: "Unnamed"
  level:
    type: int
    range: "1..20"
    default: 1
  hit_points:
    type: int
    range: "0.."
  armor_class:
    type: int
    derived: "{{ 10 + this.dexterity_modifier + this.armor_bonus }}"
  inventory:
    type: list
    of: item
```

### Attribute Fields

Each attribute definition can include the following fields:

- **`type`** (required): The data type of the attribute
- **`default`** (optional): Default value if not specified
- **`range`** (optional): Valid range for numeric types
- **`enum`** (optional): List of allowed values for string types
- **`derived`** (optional): Formula for calculated attributes
- **`of`** (optional): Element type for list attributes
- **`optional`** (optional): Whether the attribute can be null/undefined

### Data Types

#### Basic Types

- **`str`**: String/text values
- **`int`**: Integer numbers
- **`float`**: Decimal numbers
- **`bool`**: Boolean true/false values
- **`roll`**: Dice roll expressions (e.g., "2d6+3")
- **`roll_result`**: Result object from dice roll execution containing total, details, and metadata

#### Collection Types

- **`list`**: Ordered array of values
- **`dict`**: Key-value dictionary

#### Model Types

Any model ID can be used as a type to reference other models.

### Ranges

Numeric attributes can specify valid ranges using range notation:

```yaml
# Exact range
level: { type: int, range: "1..10" }

# Open-ended ranges
experience: { type: int, range: "0.." }
penalty: { type: int, range: "..0" }

# Relative ranges (using other attributes)
current_hp: { type: int, range: "0..{{ this.max_hp }}" }
```

### Derived Attributes

Derived attributes are calculated from other attributes using expression syntax:

```yaml
armor_defense:
  type: int
  derived: "{{ 10 + this.abilities.dex.bonus }}"

total_weight:
  type: float
  derived: "{{ this.inventory | map(attribute='weight') | sum }}"
```

Derived attribute expressions support the Jinja2 templating syntax, including:

- Attribute references using `this.attribute.path` syntax within `{{ }}` templates
- Basic arithmetic operations (`+`, `-`, `*`, `/`)
- Function calls like `sum()`, `max()`, `min()`
- Pipe operations for data transformation

### Nested Attributes

Attributes can contain nested structures:

```yaml
abilities:
  strength:
    score: { type: int, range: "3..18" }
    modifier: { type: int, derived: "(this.abilities.strength.score - 10) / 2" }
  dexterity:
    score: { type: int, range: "3..18" }
    modifier:
      { type: int, derived: "(this.abilities.dexterity.score - 10) / 2" }
```

## Model Inheritance

Models can inherit attributes from other models using the `extends` field:

```yaml
# Base item model
id: item
attributes:
  name: { type: str }
  weight: { type: float, default: 1.0 }
  cost: { type: int, default: 0 }

# Weapon extends item
id: weapon
extends: [item]
attributes:
  damage: { type: roll }
  weapon_type: { type: str, enum: ["melee", "ranged"] }
```

### Inheritance Rules

1. Child models inherit all attributes from parent models
2. Child models can override parent attributes
3. Multiple inheritance is supported via array notation
4. Inheritance is resolved in the order specified in the `extends` array. Later models override fields from earlier ones where conflicts occur.

## Validations

Validation rules ensure that model instances satisfy game logic constraints. Each validation rule includes both an expression and a descriptive message:

```yaml
validations:
  - expression: "{{ this.current_hit_points <= this.max_hit_points }}"
    message: "Current HP cannot exceed maximum HP"
  - expression: "{{ this.level >= 1 }}"
    message: "Character level must be at least 1"
  - expression: "{{ this.inventory | map(attribute='weight') | sum <= this.carrying_capacity }}"
    message: "Inventory weight cannot exceed carrying capacity"
  - expression: "{{ this.abilities.strength.score >= 3 && this.abilities.strength.score <= 18 }}"
    message: "Strength score must be between 3 and 18"
```

### Validation Rule Fields

Each validation rule must include:

- **`expression`** (required): Boolean expression that must evaluate to true for valid instances
- **`message`** (required): Human-readable error message displayed when validation fails

### Validation Syntax

Validation expressions use the same syntax as derived attributes and must evaluate to boolean results. Common patterns include:

- **Comparisons**: `<=`, `>=`, `<`, `>`, `==`, `!=`
- **Logical operators**: `&&` (and), `||` (or), `!` (not)
- **Function calls**: `sum()`, `count()`, `contains()`, `length`
- **Attribute references**: `this.attribute.path` within `{{ }}` templates
- **Collection operations**: `| map(attribute='property') | sum`, `| count()`, `| max(attribute='property')`

## File Naming and Location

- **Filename**: `{model_id}.yaml`
- **Location**: `models/` subdirectory within the system directory
- **Path Pattern**: `systems/{system_id}/models/{model_id}.yaml`

## Example

```yaml
id: "character"
kind: "model"
name: "Player Character"
description: "Represents a player character in the game system"
version: 1

attributes:
  # Basic information
  name: { type: str }
  level: { type: int, default: 1, range: "1..20" }

  # Abilities
  abilities:
    strength:
      bonus: { type: int, range: "1..10" }
      defense: { type: int, derived: "{{ this.bonus + 10 }}" }
    dexterity:
      bonus: { type: int, range: "1..10" }
      defense: { type: int, derived: "{{ this.bonus + 10 }}" }

  # Health
  max_hit_points: { type: int, range: "1.." }
  current_hit_points: { type: int, range: "0..$max_hit_points" }

  # Derived stats
  armor_class:
    { type: int, derived: "{{ 10 + this.abilities.dexterity.bonus }}" }

  # Inventory
  inventory: { type: list, of: "item" }
  carrying_capacity:
    { type: int, derived: "{{ this.abilities.strength.bonus * 10 }}" }

validations:
  - expression: "{{ this.current_hit_points <= this.max_hit_points }}"
    message: "Current HP cannot exceed maximum HP"
  - expression: "{{ this.inventory | map(attribute='weight') | sum <= this.carrying_capacity }}"
    message: "Inventory weight cannot exceed carrying capacity"
  - expression: "{{ this.level >= 1 }}"
    message: "Character level must be at least 1"
```

## Validation Rules

1. The `id` field must be unique within the system
2. The `kind` field must exactly match `"model"`
3. All referenced models in `extends` must exist
4. Attribute types must be valid data types or existing model IDs
5. Derived attribute expressions must be syntactically valid
6. Validation expressions must evaluate to boolean results
7. The file must be valid YAML syntax
