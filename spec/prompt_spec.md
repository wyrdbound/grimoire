# GRIMOIRE Prompt Definition Specification

## Overview

Prompt Definition files contain templates for AI-generated content in GRIMOIRE systems. These templates define how Large Language Models (LLMs) should generate descriptions, narratives, and other text content that enhances the tabletop RPG experience. Prompts provide structured templates with variable substitution to create contextually appropriate content.

Prompt templates are used by flows during `llm_generation` steps to create dynamic content based on game state and player choices.

## File Structure

All prompt definition files must follow this top-level structure:

```yaml
id: prompt_identifier
kind: prompt
name: "Human Readable Prompt Name"
description: "Description of what this prompt generates"
version: 1
llm: {}
prompt_template: |
  Template content with {{ variable }} substitution
```

### Top-Level Fields

- **`id`** (required): Unique identifier for the prompt within the system
- **`kind`** (required): Must be `"prompt"` to indicate this file defines a prompt template
- **`name`** (required): Human-readable name for the prompt
- **`description`** (optional): Detailed description of what the prompt generates
- **`version`** (optional): Version number for the prompt definition
- **`llm`** (optional): LLM configuration settings specific to this prompt
- **`prompt_template`** (required): The template content with variable substitution

## LLM Configuration

The `llm` section provides default settings for the Language Model when using this prompt:

```yaml
llm:
  provider: "ollama" # LLM provider (ollama, anthropic, openai, etc.)
  model: "gemma2" # Specific model name
  temperature: 0.7 # Creativity/randomness (0.0-1.0)
  max_tokens: 500 # Maximum response length
  system_prompt: | # Optional system-level instructions
    You are an expert dungeon master for tabletop RPGs.
```

### LLM Fields

- **`provider`** (optional): The LLM service provider to use
- **`model`** (optional): Specific model name within the provider
- **`temperature`** (optional): Controls randomness (0.0 = deterministic, 1.0 = very creative)
- **`max_tokens`** (optional): Maximum length of generated response
- **`system_prompt`** (optional): System-level instructions for the model

## Prompt Templates

The `prompt_template` field contains the actual template with variable substitution:

```yaml
prompt_template: |
  Please generate a character description for:

  Name: {{ name }}
  Gender: {{ gender }}
  Physique: {{ physique }}
  Background: {{ background }}

  Create a {{ word_count | default(100) }}-word description that captures
  their personality and appearance. Use {{ tone | default("neutral") }} tone.
```

### Variable Substitution

Templates support Jinja2-style variable substitution:

- **Simple variables**: `{{ variable_name }}`
- **Nested attributes**: `{{ character.abilities.strength.bonus }}`
- **Default values**: `{{ variable | default("fallback") }}`
- **Filters**: `{{ name | title }}`, `{{ list | join(", ") }}`

### Common Template Patterns

#### Character Description

```yaml
prompt_template: |
  Create a character description for {{ name }}, a {{ gender }} with:
  - Physique: {{ physique }}
  - Face: {{ face }}
  - Background: {{ background }}

  Write ~{{ word_count | default(125) }} words focusing on their appearance and personality.
```

#### Item Description

```yaml
prompt_template: |
  Describe this {{ item_type }}:

  Name: {{ name }}
  Quality: {{ quality }}
  {% if magical %}Special Properties: {{ magical_properties }}{% endif %}

  Provide a vivid description suitable for {{ system_name }}.
```

#### Narrative Scene

```yaml
prompt_template: |
  Set the scene for the players:

  Location: {{ location }}
  Atmosphere: {{ atmosphere }}
  Time of Day: {{ time_of_day }}

  Create an atmospheric description that draws players into the scene.
```

## File Naming and Location

- **Filename**: Should use kebab-case with `.yaml` extension
- **Location**: Must be placed in the `prompts/` directory
- **Path Pattern**: `systems/{system_id}/prompts/{prompt_id}.yaml`

## Examples

### Character Description Prompt

```yaml
id: "character_description"
kind: "prompt"
name: "Character Description Generator"
description: "Generates descriptive text for newly created characters"
version: "1.0"

llm:
  provider: "ollama"
  model: "gemma2"
  temperature: 0.8
  max_tokens: 200

prompt_template: |
  Create a character description for a {{ system_name }} character:

  Name: {{ name }}
  Gender: {{ gender }}
  Traits:
  - Physique: {{ physique }}
  - Face: {{ face }}
  - Background: {{ background }}

  Write approximately {{ word_count | default(125) }} words describing their 
  appearance, mannerisms, and personality. Match the tone and style of 
  {{ system_name }}.
```

### Location Description Prompt

```yaml
id: "location_description"
kind: "prompt"
name: "Location Description Generator"
description: "Creates atmospheric descriptions for game locations"
version: "1.0"

llm:
  provider: "anthropic"
  model: "claude-3-haiku"
  temperature: 0.7

prompt_template: |
  Describe this location for the players:

  {% if location_type %}Type: {{ location_type }}{% endif %}
  {% if atmosphere %}Atmosphere: {{ atmosphere }}{% endif %}
  {% if notable_features %}Features: {{ notable_features | join(", ") }}{% endif %}

  Create an evocative description that sets the mood and helps players
  visualize the space. Focus on sensory details and atmosphere.
```

## Integration with Flows

Prompts are referenced in flows using the `llm_generation` step type:

```yaml
- id: generate_description
  type: llm_generation
  prompt_id: character_description
  prompt_data:
    name: "{{ outputs.character.name }}"
    gender: "{{ outputs.character.gender }}"
    physique: "{{ outputs.character.traits.physique }}"
  actions:
    - set_value:
        path: "outputs.character.description"
        value: "{{ result }}"
```

## Validation Rules

1. The `kind` field must exactly match `"prompt"`
2. The `prompt_template` must be valid Jinja2 template syntax
3. All variable references in templates should be documented
4. LLM provider and model combinations must be supported
5. The file must be valid YAML syntax

## Best Practices

- Use descriptive variable names that match the game system's terminology
- Provide default values for optional variables
- Include examples in the prompt to guide the LLM's output style
- Keep prompts focused on a single type of content generation
- Test prompts with various input combinations
- Include system-specific terminology and tone guidance
- Consider token limits when designing longer prompts
