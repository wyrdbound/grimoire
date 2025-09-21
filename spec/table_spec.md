# GRIMOIRE Table Definition Specification

## Overview

Table Definition files define random generation tables for creating content in tabletop RPG systems. Tables are used to randomly select traits, generate equipment, determine outcomes, or create any other randomized content during gameplay. They support various dice types and can be referenced by flows, other tables, or directly by the game engine.

Tables provide a structured way to encode the random generation mechanics that are central to many tabletop RPGs.

## File Structure

All table definition files must follow this top-level structure:

```yaml
kind: table
id: table_identifier
name: "Human Readable Table Name"
version: 1
roll: "dice_expression"
description: "Description of what this table generates"
entry_type: "str" # Optional, defaults to "str" for string values. Set to model ID for structured data (e.g., "armor", "weapon")
entries: {}
```

### Top-Level Fields

- **`kind`** (required): Must be `"table"` to indicate this file defines a table
- **`id`** (required): Unique identifier for the table within the system
- **`name`** (optional): Human-readable name for display purposes
- **`version`** (optional): Version number for the table definition
- **`roll`** (required): Dice expression that determines how to roll on this table
- **`description`** (optional): Description of what the table generates or represents
- **`entry_type`** (optional): Type of entries returned by this table. Defaults to `"str"` for simple string values. Set to a model ID (e.g., `"armor"`, `"weapon"`, `"item"`) when the table returns structured data based on a specific model.
- **`entries`** (required): Map of roll results to their corresponding values

## Roll Expressions

The `roll` field specifies what dice to roll when using this table. GRIMOIRE uses the [wyrdbound-dice](https://github.com/wyrdbound/wyrdbound-dice) library for dice expressions, which supports standard dice notation plus advanced features:

```yaml
# Standard dice expressions
roll: "1d6"        # Roll one six-sided die
roll: "2d10"       # Roll two ten-sided dice and sum them
roll: "1d20"       # Roll one twenty-sided die
roll: "3d6"        # Roll three six-sided dice and sum them

# Advanced expressions (see wyrdbound-dice documentation for full syntax)
roll: "3d6kl1"     # Roll 3d6, keep lowest 1 die
roll: "2d20kh1"    # Roll 2d20, keep highest 1 die (advantage)
roll: "1d8r<5"     # Roll 1d8, reroll results below 5
```

For complete dice expression syntax and advanced features, refer to the [wyrdbound-dice README](https://github.com/wyrdbound/wyrdbound-dice).

### Supported Dice Types

The system supports any number of faces on dice, not just standard polyhedral dice:

- **Standard RPG Dice**: 1d4, 1d6, 1d8, 1d10, 1d12, 1d20, 1d100
- **Custom Dice**: Any number of faces (1d2, 1d3, 1d5, 1d7, 1d13, 1d30, etc.)
- **Multiple Dice**: Any number of dice (1d6, 2d6, 10d6, etc.)
- **Modifiers**: Addition and subtraction (+3, -2, etc.)

The underlying dice engine ([wyrdbound-dice](https://github.com/wyrdbound/wyrdbound-dice)) supports arbitrary face counts, so tables can use any dice expression that fits the content being generated.

## Entries

The entries section maps dice roll results to their corresponding values:

```yaml
entries:
  1: "Athletic"
  2: "Brawny"
  3: "Corpulent"
  4: "Delicate"
  5: "Gaunt"
  6: "Hulking"
```

### Entry Formats

#### Simple Values

```yaml
entries:
  1: "Red"
  2: "Blue"
  3: "Green"
  4: "Yellow"
```

#### Complex Objects

```yaml
entries:
  1:
    name: "Longsword"
    cost: 15
    damage: "1d8"
  2:
    name: "Dagger"
    cost: 2
    damage: "1d4"
```

#### Range Entries

For tables with large ranges, you can specify ranges:

```yaml
entries:
  1-10: "Common"
  11-18: "Uncommon"
  19-20: "Rare"
```

### Entry Keys

Entry keys must correspond to possible results of the roll expression:

```yaml
# For 1d6 roll
entries:
  1: "Result One"
  2: "Result Two"
  3: "Result Three"
  4: "Result Four"
  5: "Result Five"
  6: "Result Six"

# For 2d6 roll (results 2-12)
entries:
  2: "Snake Eyes"
  3: "Low Roll"
  # ... entries for 4-11
  12: "Boxcars"
```

## Table Types

### Trait Tables

Generate character traits, personality aspects, or physical descriptions:

```yaml
kind: "table"
id: "personality"
name: "Personality Traits"
roll: "1d20"
description: "Random personality traits for characters"
entries:
  1: "Ambitious"
  2: "Cautious"
  3: "Cheerful"
  # ...
```

### Equipment Tables

Generate random equipment, treasure, or loot:

```yaml
kind: "table"
id: "starting-gear"
name: "Starting Equipment"
roll: "1d6"
description: "Random starting equipment for new characters"
entry_type: "weapon"
entries:
  # Simple string reference id (uses entry_type for compendium lookup)
  1: longsword
  2: bow
  3: staff
  # ...
```

### Event Tables

Generate random encounters, weather, or story events:

```yaml
kind: "table"
id: "random-encounters"
name: "Wilderness Encounters"
roll: "1d12"
description: "Random encounters while traveling"
entries:
  1: "Pack of wolves"
  2: "Traveling merchant"
  3: "Abandoned campsite"
  # ...
```

### Nested Tables

Tables can reference other tables for complex generation:

```yaml
kind: "table"
id: "magic-item"
name: "Magic Item Generator"
roll: "1d4"
entry_type: "table"
entries:
  1: magic-weapons
  2: magic-armor
  3: potions
  4: scrolls
```

## Weighted Tables

For non-uniform probability distributions, use different dice or multiple entries:

```yaml
# Using d100 for fine-grained probability
kind: "table"
id: "treasure-rarity"
name: "Treasure Rarity"
roll: "1d100"
entries:
  1-50: "Common" # 50% chance
  51-80: "Uncommon" # 30% chance
  81-95: "Rare" # 15% chance
  96-100: "Legendary" # 5% chance
```

## Cross-References and Dynamic Generation

Tables can reference compendium content and support dynamic generation through several mechanisms:

### Entry Type Declaration

The `entry_type` field at the top level specifies the default model type for all entries:

```yaml
kind: "table"
id: "starting-gear"
name: "Starting Gear"
roll: "1d20"
entry_type: "item" # Default model type for entries
entries:
  1: "longsword" # Uses entry_type (item) for compendium lookup
  2: "leather" # Uses entry_type (item) for compendium lookup
  3: { id: "steel_sword", type: "weapon" } # Overrides entry_type
```

- **Default**: `entry_type` defaults to `"str"` for simple string values
- **Model References**: Set to a model ID (e.g., `"armor"`, `"weapon"`, `"item"`) for structured data
- **Overrides**: Individual entries can override the table's `entry_type`

### Entry Formats

#### Simple ID Reference

```yaml
entries:
  1: "longsword" # Uses table's entry_type for compendium lookup
```

#### Explicit Type Override

```yaml
entries:
  1: { id: "longsword", type: "weapon" } # Overrides table's entry_type
  2: { id: "leather_armor", type: "armor" }
```

#### Random Selection from Type

```yaml
entries:
  1: { type: "weapon" } # Random weapon from compendium
  2: { type: "armor" } # Random armor from compendium
```

#### Dynamic Generation

```yaml
entries:
  1: { generate: true } # Generate using table's entry_type
  2: { type: "weapon", generate: true } # Generate new weapon
  3: { type: "armor", generate: true } # Generate new armor
```

### Complete Example

```yaml
kind: "table"
id: "starting-gear"
name: "Starting Gear"
roll: "1d20"
entry_type: "item" # Default model type
entries:
  # Simple references (uses entry_type: item)
  1: "longsword"
  2: "leather_armor"
  3: "backpack"

  # Explicit type overrides
  4: { id: "steel_sword", type: "weapon" }
  5: { id: "plate_mail", type: "armor" }

  # Random selections from specific types
  10: { type: "weapon" } # Random weapon from compendium
  11: { type: "armor" } # Random armor from compendium
  12: { type: "item" } # Random item from compendium

  # Dynamic generation
  17: { type: "item" } # Random existing item
  18: { generate: true } # Generate new item (uses entry_type)
  19: { type: "armor", generate: true } # Generate new armor
  20: { type: "weapon", generate: true } # Generate new weapon
```

### Resolution Rules

1. **Simple String**: Uses table's `entry_type` for compendium lookup
2. **Explicit ID**: If `type` specified, uses that type; otherwise uses `entry_type`
3. **Random Selection**: If no `id` but `type` specified, selects random compendium entry for that type
4. **Generation**: If `generate: true`, engine attempts to create new content based on:
   - Existing compendium entries for the specified type
   - Model structure and constraints
   - System-specific generation rules

### Backward Compatibility

This design maintains full backward compatibility:

- Existing tables without `entry_type` continue to work (defaults to `"str"`)
- Simple string entries continue to work as before
- Complex object entries continue to work as before

## File Naming and Location

- **Filename**: Descriptive name with `.yaml` extension
- **Location**: `tables/` subdirectory within the system directory
- **Path Pattern**: `systems/{system_id}/tables/{category}/{filename}.yaml`
- **Subdirectories**: Recommended subcategorization (e.g., `traits/`, `gear/`, `encounters/`)

## Example

```yaml
kind: "table"
id: "character-background"
name: "Character Background"
version: "1.0"
roll: "1d10"
description: "Random backgrounds for character creation"

entries:
  1: "Blacksmith"
  2: "Farmer"
  3: "Merchant"
  4: "Scholar"
  5: "Soldier"
  6: "Thief"
  7: "Hunter"
  8: "Sailor"
  9: "Herbalist"
  10: "Entertainer"
```

## Validation Rules

1. The `kind` field must exactly match `"table"`
2. The `id` field must be unique within the system
3. The `roll` field must be a valid dice expression
4. All entry keys must be valid results for the specified dice roll
5. Entry keys must cover all possible roll results (no gaps)
6. Range entries (e.g., "1-5") must not overlap
7. Referenced tables or content must exist
8. The file must be valid YAML syntax
