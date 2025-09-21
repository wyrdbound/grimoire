# GRIMOIRE Source Definition Specification

## Overview

Source Definition files provide metadata about the original rulebooks, supplements, or other materials that game content is derived from. They serve as bibliographic references that track the provenance of models, tables, compendiums, and other system content. This enables proper attribution and helps organize content by its source material.

Source files act as a registry of the books, PDFs, websites, or other materials that contribute content to a GRIMOIRE system.

## File Structure

All source definition files must follow this top-level structure:

```yaml
id: "unique_source_identifier"
kind: "source"
name: "Human Readable Source Name"
description: "Description of the source material"
version: 1
edition: "Edition or Version"
publisher: "Publishing Company"
source_url: "https://example.com/source"
isbn: "978-0-123456-78-9" # optional
publication_date: "2023" # optional
authors: [] # optional
license: "License Type" # optional
```

### Top-Level Fields

- **`id`** (required): Unique identifier for the source within the system
- **`kind`** (required): Must be `"source"` to indicate this file defines a source
- **`name`** (required): Human-readable name of the source material
- **`description`** (optional): Detailed description of what the source contains
- **`version`** (optional): Version number for the source definition
- **`edition`** (optional): Edition, version, or printing information
- **`publisher`** (optional): Company or entity that published the material
- **`source_url`** (optional): Official website, store page, or download link
- **`isbn`** (optional): ISBN number for books
- **`publication_date`** (optional): Year or date of publication
- **`authors`** (optional): Array of author names
- **`license`** (optional): License or copyright information

## Source Types

### Core Rulebooks

Primary game system books that contain foundational rules:

```yaml
id: core-rulebook
kind: source
name: "My RPG Core Rulebook"
description: "The main rulebook containing character creation, basic rules, and GM guidance"
edition: "2nd Edition"
publisher: "Example Games Publishing"
authors: ["Jane Smith", "John Doe"]
publication_date: "2023"
isbn: "978-0-123456-78-9"
```

### Supplements and Expansions

Additional books that expand the game system:

```yaml
id: advanced-magic
kind: source
name: "Advanced Magic Supplement"
description: "Expanded spellcasting rules and new magical items"
edition: "1st Edition"
publisher: "Example Games Publishing"
authors: ["Jane Smith"]
publication_date: "2024"
```

### Third-Party Content

Community or third-party created materials:

```yaml
id: community-bestiary
kind: source
name: "Community Monster Manual"
description: "Fan-created monsters and encounters"
publisher: "RPG Community"
authors: ["Various Contributors"]
license: "Creative Commons Attribution 4.0"
source_url: "https://rpgcommunity.com/monsters"
```

### Digital Sources

Online content, PDFs, or digital-only materials:

```yaml
id: web-supplement
kind: source
name: "Online Equipment Database"
description: "Comprehensive equipment and gear database"
publisher: "Digital RPG Tools"
source_url: "https://digitalrpg.com/equipment"
license: "Open Game License v1.0a"
```

### Official Errata and Updates

Official corrections or updates to published materials:

```yaml
id: "errata-2024"
kind: source
name: "2024 Official Errata"
description: "Official corrections and clarifications for the core rulebook"
publisher: "Example Games Publishing"
publication_date: "2024"
source_url: "https://examplegames.com/errata"
```

## Referencing Sources

Other files in the system can reference sources to indicate their origin:

### In Models

```yaml
# character.yaml
id: character
kind: model
name: Character
source: core-rulebook # References the source
# ... rest of model definition
```

### In Compendiums

```yaml
# weapons.yaml
kind: compendium
name: basic-weapons
model: weapon
source: core-rulebook
# ... entries
```

### In Tables

```yaml
# traits.yaml
kind: table
name: personality-traits
source: core-rulebook
# ... table definition
```

## Multi-Source Content

Content can be derived from multiple sources:

```yaml
# In a model or compendium file
sources:
  - "core-rulebook"
  - "advanced-magic"
  - "errata-2024"
```

## Author Information

Authors can be specified in various formats:

```yaml
# Single author
authors: ["Jane Smith"]

# Multiple authors
authors: ["Jane Smith", "John Doe", "Alice Johnson"]

# Authors with roles
authors:
  - name: "Jane Smith"
    role: "Lead Designer"
  - name: "John Doe"
    role: "Artist"
  - name: "Alice Johnson"
    role: "Editor"
```

## License Information

Common license types for tabletop RPG content:

```yaml
# Open licenses
license: "Creative Commons Attribution 4.0"
license: "Open Game License v1.0a"
license: "Creative Commons Attribution-ShareAlike 4.0"

# Proprietary licenses
license: "All Rights Reserved"
license: "Used with Permission"

# Custom licenses
license: "Example Games Community License"
```

## Publication Dates

Publication dates can be specified in various formats:

```yaml
publication_date: "2023"           # Year only
publication_date: "2023-06"        # Year and month
publication_date: "2023-06-15"     # Full date
publication_date: "June 2023"      # Formatted string
```

## File Naming and Location

- **Filename**: Descriptive name with `.yaml` extension
- **Location**: `sources/` subdirectory within the system directory
- **Path Pattern**: `systems/{system_id}/sources/{filename}.yaml`
- **Naming Convention**: Use descriptive names that reflect the source material

## Example

```yaml
id: players-handbook
kind: source
name: "Player's Handbook"
description: "The essential rules and character options for players"
edition: "5th Edition"
publisher: "Wizards of the Coast"
authors:
  - "Mike Mearls"
  - "Jeremy Crawford"
  - "Chris Perkins"
publication_date: "2014"
isbn: "978-0-7869-6560-1"
source_url: "https://dnd.wizards.com/products/tabletop/players-basic-rules"
license: "All Rights Reserved"
```

## Integration with System

### Default Source

Systems can specify a default source in their `system.yaml`:

```yaml
# system.yaml
id: my-rpg
kind: system
name: "My RPG System"
default_source: core-rulebook
# ...
```

### Source Validation

When content references a source, the system validates:

1. The referenced source exists
2. The source ID matches an existing source file
3. The source file is valid and properly formatted

### Content Organization

Sources help organize content by:

- **Attribution**: Proper credit to original creators
- **Filtering**: Show only content from specific sources
- **Licensing**: Track usage rights and restrictions
- **Updates**: Identify content that needs updates when sources change

## Validation Rules

1. The `id` field must be unique within the system
2. The `kind` field must exactly match `"source"`
3. The `name` field is required and should be descriptive
4. URLs in `source_url` should be valid HTTP/HTTPS links
5. ISBN numbers should follow proper ISBN format if provided
6. Publication dates should use consistent formatting
7. The file must be valid YAML syntax
