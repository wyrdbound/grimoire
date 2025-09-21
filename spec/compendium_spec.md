# GRIMOIRE Compendium Definition Specification

## Overview

Compendium Definition files contain collections of game content instances based on defined models. They serve as databases of items, spells, monsters, or other game entities that can be referenced and used during gameplay. Compendiums organize related content and make it easily accessible to the game engine.

Each compendium file contains multiple entries of the same model type, providing a centralized location for content of a specific category.

## File Structure

All compendium definition files must follow this top-level structure:

```yaml
id: "compendium_identifier"
kind: "compendium"
name: "Compendium Name"
model: "target_model_id"
entries: {}
```

### Top-Level Fields

- **`kind`** (required): Must be `"compendium"` to indicate this file defines a compendium
- **`id`** (required): Identifier for this compendium, used for referencing
- **`name`** (required): Human-readable name for the compendium, used in UI and documentation
- **`model`** (required): The model ID that all entries in this compendium must conform to
- **`entries`** (required): Map of entry instances, where keys are entry IDs and values are model instances

## Entries

The entries section contains the actual game content. Each entry must be a valid instance of the specified model:

```yaml
entries:
  longsword:
    name: "Longsword"
    description: "A versatile steel blade favored by knights"
    damage: "1d8"
    weight: 3.0
    cost: 1500
    weapon_type: "melee"

  shortbow:
    name: "Shortbow"
    description: "A compact bow suitable for hunting"
    damage: "1d6"
    weight: 2.0
    cost: 3000
    weapon_type: "ranged"
```

### Entry Structure

Each entry is defined as:

```yaml
entry_id:
  attribute1: value1
  attribute2: value2
  # ... additional attributes as defined by the model
```

#### Entry Requirements

1. **Entry ID**: Must be unique within the compendium file
2. **Required Attributes**: All non-optional model attributes must be provided
3. **Valid Values**: All attribute values must conform to the model's constraints
4. **Type Compliance**: Values must match the expected data types

### Value Types

Entries can contain various value types based on the model definition:

#### Basic Values

```yaml
item_name: "Magic Sword" # String
quantity: 5 # Integer
weight: 2.5 # Float
magical: true # Boolean
damage: "2d6+1" # Dice roll
```

#### Lists

```yaml
tags: ["weapon", "magical", "rare"]
materials: ["steel", "silver"]
```

#### Nested Objects

```yaml
properties:
  durability: 85
  enchantment_level: 3
  special_abilities: ["flame", "keen_edge"]
```

### Inline vs Block Style

Entries can be written in different YAML styles for readability:

#### Inline Style (Compact)

```yaml
entries:
  dagger: { name: "Dagger", damage: "1d4", cost: 200, weight: 1.0 }
  club: { name: "Club", damage: "1d4", cost: 0, weight: 2.0 }
```

#### Block Style (Readable)

```yaml
entries:
  dagger:
    name: "Dagger"
    damage: "1d4"
    cost: 200
    weight: 1.0
    description: "A small, sharp blade perfect for close combat"

  club:
    name: "Club"
    damage: "1d4"
    cost: 0
    weight: 2.0
    description: "A simple wooden cudgel"
```

## Model Validation

All entries in a compendium are automatically validated against their specified model:

1. **Required Attributes**: Must be present unless they have default values
2. **Type Checking**: Values must match the expected data types
3. **Range Validation**: Numeric values must fall within specified ranges
4. **Enum Validation**: String values must be from allowed lists if specified
5. **Custom Validations**: Must satisfy any validation rules defined in the model

## Quantity and Variants

Entries can specify quantities and create variants:

```yaml
entries:
  arrows:
    name: "Arrows"
    qty: 20 # Bundle of 20 arrows
    weight: 1.0 # Total weight for the bundle
    cost: 100 # Cost for entire bundle

  healing_potion_minor:
    name: "Minor Healing Potion"
    effect: "heal 1d4+1"

  healing_potion_major:
    name: "Major Healing Potion"
    effect: "heal 2d4+2"
```

## Organizational Patterns

### By Category

```yaml
# weapons/melee.yaml
kind: compendium
name: melee-weapons
model: weapon

# weapons/ranged.yaml
kind: compendium
name: ranged-weapons
model: weapon
```

### By Rarity/Level

```yaml
# items/common-gear.yaml
kind: compendium
name: common-gear
model: item

# items/magical-items.yaml
kind: compendium
name: magical-items
model: item
```

### By Source Material

```yaml
# items/core-rulebook.yaml
kind: compendium
name: core-equipment
model: item

# items/expansion-pack.yaml
kind: compendium
name: expansion-equipment
model: item
```

## File Naming and Location

- **Filename**: Descriptive name with `.yaml` extension
- **Location**: `compendium/` subdirectory within the system directory
- **Path Pattern**: `systems/{system_id}/compendium/{category}/{filename}.yaml`
- **Subdirectories**: Optional subcategorization (e.g., `weapons/`, `armor/`, `items/`)

## Example

```yaml
kind: "compendium"
name: "basic-weapons"
model: "weapon"

entries:
  dagger:
    name: "Dagger"
    description: "A small, sharp blade suitable for close combat or throwing"
    damage: "1d4"
    weight: 1.0
    cost: 200
    weapon_type: "melee"
    tags: ["light", "finesse", "thrown"]

  longsword:
    name: "Longsword"
    description: "A versatile straight blade, well-balanced for combat"
    damage: "1d8"
    weight: 3.0
    cost: 1500
    weapon_type: "melee"
    hands: 1
    tags: ["versatile"]

  shortbow:
    name: "Shortbow"
    description: "A compact hunting bow, easy to use and carry"
    damage: "1d6"
    weight: 2.0
    cost: 2500
    weapon_type: "ranged"
    hands: 2
    range: 80
    tags: ["ammunition"]
```

## Validation Rules

1. The `kind` field must exactly match `"compendium"`
2. The `id` field must be unique within the system
3. The `model` field must reference an existing model definition
4. All entries must be valid instances of the specified model
5. Entry IDs must be unique within the compendium
6. All required model attributes must be provided (unless they have defaults)
7. All values must satisfy the model's type and validation constraints
8. The file must be valid YAML syntax
