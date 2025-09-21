# GRIMOIRE System Definition Format Specification

## Overview

The GRIMOIRE (Generic Rule Implementation Model for Omniversal Interactive Roleplaying Engines) System Definition Format is a comprehensive specification for encoding tabletop RPG systems in a structured, machine-readable format. This format enables AI-powered game masters to understand and execute the rules of various tabletop RPG systems, providing players with authentic rule-based gameplay experiences.

The format is designed to be:

- **System-agnostic**: Works with any tabletop RPG system
- **Machine-readable**: Structured for automated processing
- **Human-friendly**: Uses YAML for easy editing and maintenance
- **Extensible**: Supports custom content and system-specific mechanics
- **AI-integrated**: Includes prompt templates for LLM-assisted content generation

## File Type Specifications

### Core System Files

#### [System Definition](system_spec.md)

**File**: `system.yaml`  
**Purpose**: Root configuration file that defines the core metadata, currency system, and default settings for a tabletop RPG system.

Key features:

- System metadata and identification
- Currency and economic systems
- Attribution and licensing information
- Default source material references

#### [Flow Definition](flow_spec.md)

**Files**: `flows/*.yaml`  
**Purpose**: Defines structured rule sequences for character creation, ability checks, combat resolution, and other game mechanics.

Key features:

- Step-by-step rule execution
- LLM integration for subjective decisions
- Conditional logic and branching
- Typed input and output validation

### Reference and Content Files

#### [Source Definition](source_spec.md)

**Files**: `sources/*.yaml`  
**Purpose**: Provides bibliographic metadata about the original rulebooks and materials that content is derived from.

Key features:

- Attribution and licensing tracking
- Publication information
- Author and publisher details
- Content organization by source

#### [Prompt Definition](prompt_spec.md)

**Files**: `prompts/*.yaml`  
**Purpose**: Contains AI prompt templates for generating character descriptions, narratives, and other text content.

Key features:

- LLM configuration settings
- Variable substitution templates
- Integration with flow generation steps
- System-specific tone and style guidance

### Data Structure Files

#### [Model Definition](model_spec.md)

**Files**: `models/*.yaml`  
**Purpose**: Defines the data structures for game entities like characters, items, weapons, and other game objects.

Key features:

- Attribute definitions with types and constraints
- Model inheritance and composition
- Derived attributes and calculations
- Validation rules and business logic

#### [Compendium Definition](compendium_spec.md)

**Files**: `compendium/**/*.yaml`  
**Purpose**: Contains collections of concrete game content (items, spells, monsters, etc.) based on defined models.

Key features:

- Organized content libraries
- Model-based validation
- Searchable and filterable content
- Support for variants and quantities

#### [Table Definition](table_spec.md)

**Files**: `tables/**/*.yaml`  
**Purpose**: Defines random generation tables for traits, equipment, encounters, and other randomized content.

Key features:

- Flexible dice roll expressions
- Weighted probability distributions
- Cross-references to other content
- Support for complex nested generation

## Directory Structure

A complete GRIMOIRE system follows this directory structure:

```
systems/{system_id}/
├── system.yaml                 # System definition (required)
├── flows/                      # Flow definitions
│   ├── character_creation.yaml
│   ├── ability_check.yaml
│   └── combat_resolution.yaml
├── models/                     # Data model definitions
│   ├── character.yaml
│   ├── item.yaml
│   ├── weapon.yaml
│   └── armor.yaml
├── compendium/                 # Content libraries
│   ├── items/
│   │   ├── weapons.yaml
│   │   ├── armor.yaml
│   │   └── equipment.yaml
│   ├── spells/
│   │   └── arcane.yaml
│   └── creatures/
│       └── monsters.yaml
├── tables/                     # Random generation tables
│   ├── traits/
│   │   ├── personality.yaml
│   │   ├── background.yaml
│   │   └── appearance.yaml
│   └── generation/
│       ├── treasure.yaml
│       └── encounters.yaml
├── sources/                    # Source material references
│   ├── core-rulebook.yaml
│   └── supplement.yaml
└── prompts/                    # AI prompt templates
    ├── character-description.yaml
    ├── item-description.yaml
    └── location-description.yaml
```

## System Integration

### Loading Order

1. **Source Definitions**: Bibliographic references and attribution
2. **System Definition**: Core system metadata and configuration
3. **Model Definitions**: Data structures and validation rules
4. **Compendium Content**: Instantiated game objects and content
5. **Table Definitions**: Random generation mechanics
6. **Flow Definitions**: Rule procedures and game mechanics
7. **Prompt Definitions**: AI content generation templates

### Cross-References

Files can reference each other using consistent ID-based linking:

- Models can extend other models
- Compendiums instantiate models
- Tables can reference compendium entries
- Flows can invoke tables and manipulate models
- Sources provide attribution for all content types

### Validation

The system provides comprehensive validation:

- **Syntax Validation**: All YAML files must be syntactically correct
- **Schema Validation**: Files must conform to their type specifications
- **Reference Validation**: All cross-references must resolve to existing content
- **Business Logic Validation**: Model instances must satisfy validation rules
- **Consistency Validation**: The system must be internally consistent

## Getting Started

### Creating a New System

1. Create a system directory: `systems/{your_system_id}/`
2. Start with a `system.yaml` file defining core metadata
3. Define your core models (character, item, etc.)
4. Create compendiums with game content
5. Add tables for random generation
6. Build flows for key game mechanics
7. Include prompt templates for AI assistance

### Converting Existing Systems

1. Analyze the source material to identify key data structures
2. Create models for the primary game entities
3. Extract tables and random generation mechanics
4. Define flows for complex rule procedures
5. Create compendiums with official content
6. Add source attribution and licensing information
7. Create prompt templates for AI-assisted content generation

### Best Practices

- Start with core mechanics and expand incrementally
- Use descriptive names and include documentation
- Test with sample content to validate the structure
- Leverage model inheritance to reduce duplication
- Include comprehensive examples in tables and flows
- Provide clear AI prompts that match the system's tone

## Community and Contributions

The GRIMOIRE System Definition Format is designed to support community contributions and system sharing. Systems created using this format can be:

- Shared across different GRIMOIRE installations
- Collaboratively developed and maintained
- Extended with community content
- Adapted for different play styles and house rules

For questions, contributions, or system sharing, please refer to the main [Wyrdbound](https://github.com/wyrdbound) project documentation and community resources.
