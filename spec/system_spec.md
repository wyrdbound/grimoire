# GRIMOIRE System Definition Specification

## Overview

A System Definition file serves as the root configuration for a tabletop RPG system in GRIMOIRE. It defines the core metadata, rules, and default settings that apply to the entire game system. This file acts as the entry point for loading a system and provides essential information about currency, credits, and default sources.

System definition files are placed at the root of a system directory and must be named `system.yaml`.

## File Structure

All system definition files must follow this top-level structure:

```yaml
id: unique_system_identifier
kind: system
name: "Human Readable System Name"
description: "Description of the tabletop RPG system"
version: 1
default_source: "source_id"
currency: {}
credits: {}
```

### Top-Level Fields

- **`id`** (required): Unique identifier for the system, used for referencing
- **`kind`** (required): Must be `"system"` to indicate this file defines a system
- **`name`** (required): Human-readable name for the tabletop RPG system
- **`description`** (optional): Detailed description of the system's focus and style
- **`version`** (optional): Version number for the system definition
- **`default_source`** (optional): ID of the default source book/ruleset to reference
- **`currency`** (optional): Currency system definition for the game
- **`credits`** (optional): Attribution information for the original system

## Currency System

The currency system defines how money works within the game system:

```yaml
currency:
  base_unit: "copper" # The base unit for all calculations
  denominations:
    cp:
      name: "copper"
      symbol: "cp"
      value: 1 # Value relative to base unit
      weight: 0.05 # Weight per coin
    sp:
      name: "silver"
      symbol: "sp"
      value: 10
      weight: 0.05
    gp:
      name: "gold"
      symbol: "gp"
      value: 100
      weight: 0.05
```

### Currency Fields

- **`base_unit`** (required): The fundamental unit used for internal calculations
- **`denominations`** (required): Map of currency types with the following properties:
  - **`name`** (required): Full name of the currency
  - **`symbol`** (required): Abbreviated symbol (e.g., "gp", "cp")
  - **`value`** (required): Exchange rate relative to the base unit
  - **`weight`** (optional): Physical weight per coin in whatever unit is used in the game (e.g., grams, ounces, pounds)

## Credits

The credits section provides attribution for the original tabletop RPG system:

```yaml
credits:
  author: "Original Author Name"
  license: "License Type (e.g., CC BY 4.0, Open Game License)"
  publisher: "Publishing Company"
  source_url: "https://example.com/game"
```

### Credits Fields

All credits fields are optional but recommended:

- **`author`**: The original creator(s) of the tabletop RPG system
- **`license`**: The license under which the system is distributed
- **`publisher`**: The company or entity that published the system
- **`source_url`**: Official website or purchase link for the system

## File Naming and Location

- **Filename**: Must be `system.yaml`
- **Location**: Must be placed at the root of the system directory
- **Path Pattern**: `systems/{system_id}/system.yaml`

## Example

```yaml
id: "my_fantasy_rpg"
kind: "system"
name: "My Fantasy RPG"
description: "A classic fantasy adventure system with streamlined rules"
version: 1
default_source: "core_rulebook"

currency:
  base_unit: "copper"
  denominations:
    cp: { name: "copper", symbol: "cp", value: 1, weight: 0.05 }
    sp: { name: "silver", symbol: "sp", value: 10, weight: 0.05 }
    gp: { name: "gold", symbol: "gp", value: 100, weight: 0.05 }
    pp: { name: "platinum", symbol: "pp", value: 1000, weight: 0.05 }

credits:
  author: "Jane Smith"
  license: "Open Game License v1.0a"
  publisher: "Fantasy Games Publishing"
  source_url: "https://fantasygames.com/myfantasyrpg"
```

## Validation Rules

1. The `id` field must be unique across all systems
2. The `kind` field must exactly match `"system"`
3. Currency denominations must have positive `value` fields
4. If `default_source` is specified, a corresponding source file must exist
5. The file must be valid YAML syntax
