# GRIMOIRE Flow Definition Specification

## Overview

GRIMOIRE Flows provide a structure for defining complex rules in tabletop RPG systems, with full support for invoking LLMs to resolve fuzzy or subjective questions. In general, Flows define those points in the game where the Game Master guides the players through a specific set of rules, such as how to create a character or perform an ability check.

Flows are defined as YAML files that describe a sequence of steps, choices, and actions that can be executed by the GRIMOIRE engine. They are designed to be system-agnostic and reusable across different tabletop RPG systems.

## File Structure

All flow definition files must follow this top-level structure:

```yaml
id: unique_flow_identifier
kind: flow
name: "Human Readable Flow Name"
description: "Description of what this flow accomplishes"
version: 1

inputs: []
outputs: []
variables: []
steps: []
resume_points: []
```

### Top-Level Fields

- **`id`** (required): Unique identifier for the flow
- **`kind`** (required): Must be `flow` to indicate this file defines a flow
- **`name`** (required): Human-readable name for the flow
- **`description`** (optional): Detailed description of the flow's purpose
- **`version`** (optional): Version number for the flow definition. Defaults to `1` if not specified.
- **`inputs`** (optional): Array of input parameters the flow expects
- **`outputs`** (optional): Array of output objects the flow produces
- **`variables`** (optional): Local variables used during flow execution
- **`steps`** (required): Array of steps that define the flow logic
- **`resume_points`** (optional): Array of step IDs where flow execution can be resumed

## Inputs, Outputs, and Variables

Each input/output/variable definition includes:

- **`type`**: The data type (model name, or basic types like `str`, `int`, `bool`, `float`, `list`, `dict`)
- **`id`**: Reference identifier used within the flow
- **`required`** (inputs only): Whether the input is mandatory
- **`validate`** (outputs only): Whether to run validation on the output

### Inputs

Inputs allow the flow to be passed existing data from the caller.

```yaml
inputs:
  - type: character
    id: existing_character
    required: true
  - type: str
    id: player_name
    required: false
```

### Outputs

Outputs allow the flow to return data to the caller.

```yaml
outputs:
  - type: character
    id: new_character
    validate: true
```

### Variables

Local variables provide temporary storage during flow execution:

```yaml
variables:
  - type: str
    id: hp_dice_roll
    validate: true
  - type: list
    id: selected_items
    validate: true
  - type: int
    id: calculation_result
    validate: true
```

Variables can be referenced using `variables.variable_name` syntax in templates.

## Steps

Steps are the core building blocks of flows. Each step has a consistent structure:

```yaml
- id: step_identifier
  name: "Human Readable Step Name"
  type: step_type
  prompt: "Text displayed to the user"
  condition: optional_condition
  parallel: true # optional
  pre_actions: [] # optional - actions to run before step execution
  actions: []
  next_step: next_step_id # optional
```

### Step Types

#### `dice_roll`

Performs a single dice roll using the [wyrdbound-dice](https://github.com/wyrdbound/wyrdbound-dice) library.

```yaml
- id: roll_damage
  type: dice_roll
  prompt: "Roll for damage..."
  roll: "2d6+3"
  actions:
    - set_value:
        path: "outputs.damage_dealt"
        value: "{{ result.total }}"
    - log_message:
        message: "Rolled {{ result.detail }}"
```

**Roll Expression**: The `roll` field supports the full [wyrdbound-dice](https://github.com/wyrdbound/wyrdbound-dice) syntax, including advanced features like keep highest/lowest (e.g., `3d6kl1`, `2d20kh1`) and rerolls (e.g., `1d8r<5`).

**Roll Result Object**: The `result` contains:

- **`total`**: The final numeric result of the roll
- **`detail`**: A string showing the breakdown of the roll (e.g., "2d6+3: [4,5]+3 = 12")

#### `dice_sequence`

Performs multiple dice rolls in sequence using the [wyrdbound-dice](https://github.com/wyrdbound/wyrdbound-dice) library.

```yaml
- id: roll_abilities
  type: dice_sequence
  sequence:
    items:
      [
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma",
      ]
    roll: 4d6kh3
    actions:
      - set_value:
          path: "outputs.character.abilities.{{ item }}.bonus"
          value: "{{ result.total }}"
      - log_message:
          message: "{{ item|title }}: {{ result.total }} ({{ result.detail }})"
```

#### `player_choice`

Presents choices to the player.

```yaml
- id: choose_action
  type: player_choice
  prompt: "What do you want to do?"
  pre_actions:
    - display_value: "variables.current_status"
  choices:
    - id: attack
      label: "Attack with weapon"
      actions:
        - set_value:
            path: "variables.chosen_action"
            value: "attack"
      next_step: resolve_attack
    - id: defend
      label: "Defend and gain bonus"
      actions:
        - set_value:
            path: "variables.chosen_action"
            value: "defend"
      next_step: resolve_defense
    - id: restart
      label: "Start over"
      next_step: beginning
```

Choice sources can also be dynamic:

```yaml
# From a table
choice_source:
  table: treasure_rarity_c
  display_format: "{{ entry.name|title }}"
  selection_count: 3 # Default is 1
```

```yaml
# From values existing in the context
choice_source:
  table_from_values: "outputs.character.abilities"
  display_format: "{{ key|title }}: +{{ value.bonus }}"
  selection_count: 2
```

#### `table_roll`

Rolls on predefined tables.

```yaml
- id: random_encounter
  type: table_roll
  prompt: "Rolling for random encounter..."
  tables:
    - table: encounter_type_table
      actions:
        - set_value:
            path: "variables.encounter_type"
            value: "{{ result.entry }}"
        - log_message:
            message: "Encountered: {{ result.entry }} ({{ result.roll_result.detail }})"
```

**Table Roll Result Object**: The `result` contains:

- **`entry`**: The selected entry from the table
- **`roll_result`**: The dice roll result object with `total` and `detail` fields

#### `player_input`

Prompts the player for text input.

```yaml
- id: get_character_name
  type: player_input
  prompt: "What is your character's name?"
  actions:
    - set_value:
        path: "outputs.character.name"
        value: "{{ result }}"
```

The player's input is available in templates as `{{ result }}`, maintaining consistency with other step types. This step type is ideal for collecting names, descriptions, or any custom text from the player.

#### `llm_generation`

Uses Large Language Models to generate content.

```yaml
- id: generate_description
  type: llm_generation
  condition: llm_enabled
  prompt_id: character_description_prompt
  prompt_data:
    traits: "{{ outputs.character.traits }}"
    background: "{{ outputs.character.background }}"
  llm_settings:
    provider: anthropic
    model: claude-3-haiku
    max_tokens: 200
  actions:
    - set_value:
        path: "outputs.character.description"
        value: "{{ result }}"
```

#### `name_generation`

Generates random names using a requested generator. Defaults to the [wyrdbound-rng](https://github.com/wyrdbound/wyrdbound-rng) library.

```yaml
- id: generate_character_name
  type: name_generation
  prompt: "Generating a random name for your character..."
  generator: wyrdbound-rng
  settings:
    max_length: 12
    corpus: generic-fantasy
    segmenter: fantasy
    algorithm: bayesian
    min_probability: 1e-4
    best_of: 2
  actions:
    - set_value:
        path: "outputs.character_name"
        value: "{{ result.name }}"
```

**Configuration Options:**

- **`generator`** (optional): Identifier for the name generator. Defaults to `"wyrdbound-rng"` if not specified. Currently, `"wyrdbound-rng"` is the only supported generator.
- **`settings`** (optional): Configuration parameters for name generation. The available settings depend on the generator being used:

**Settings for `wyrdbound-rng` generator:**

- **`max_length`** (optional): Maximum length of the generated name. Defaults to 15.
- **`corpus`** (optional): The name corpus/data file to use. Defaults to `"generic-fantasy"`. Must be a valid corpus available in wyrdbound-rng.
- **`segmenter`** (optional): The segmentation strategy to use. Defaults to `"fantasy"`.
- **`algorithm`** (optional): The generation algorithm to use. Defaults to `"bayesian"`.
- **`min_probability`** (optional): Minimum probability threshold for generated names (for bayesian algorithm only).
- **`best_of`** (optional): Number of names to generate and select the best from (for bayesian algorithm only).

The generated name object is always available as `{{ result }}` in templates. To access just the name string, use `{{ result.name }}`.

#### `completion`

Marks the end of a flow. Useful when there are conditional branches in the flow and you want to ensure a clean exit point.

```yaml
- id: finish
  type: completion
  prompt: "Character creation complete!"
  actions:
    - log_event:
        type: character_created
        data: "{{ outputs.new_character.name }}"
```

#### `conditional_branch`

Provides conditional logic with if-then-else branching within a flow step. Allows for dynamic execution paths based on evaluated conditions.

Each `then` and `else` block is a **structured object** with two optional keys:

- **`actions`**: List of actions to run when the branch is taken
- **`next_step`**: Step ID to jump to after the branch executes (overrides the step-level `next_step`)

Both keys are optional. An `else` block with only `next_step` and no `actions` is a pure routing branch.

```yaml
# Pattern 1: match/skip — jump directly on match, fall through on miss
- id: set_base_hp_warrior
  type: conditional_branch
  if: "{{ inputs.character_class == 'warrior' }}"
  then:
    actions:
      - set_value:
          path: "variables.base_hp"
          value: "12"
    next_step: compute_hp       # jump past remaining class checks
  else:
    next_step: set_base_hp_rogue  # check next class

# Pattern 2: branch with actions on both sides
- id: check_afford
  type: conditional_branch
  if: "{{ variables.gold < variables.last_item_cost }}"
  then:
    actions:
      - display_message: "❌ You can't afford that."
    next_step: shop_menu
  else:
    next_step: deduct_gold

# Pattern 3: step-level next_step (applies when then/else don't specify one)
- id: calculate_spell_slots
  type: conditional_branch
  if: "{{ outputs.character.character_class == 'mage' }}"
  then:
    actions:
      - set_value:
          path: "outputs.character.spell_slots.max"
          value: "{{ 3 + outputs.character.mind.modifier }}"
  next_step: roll_starting_gold   # reached by both branches
```

**Conditional Structure**:

- **`if`**: Jinja2 template expression that evaluates to a boolean
- **`then`**: Branch block executed when condition is true
- **`else`**: Optional branch block executed when condition is false
- **`next_step`** (step-level): Fallback used when the taken branch does not specify its own `next_step`

**Branch block fields**:

| Field | Required | Description |
|-------|----------|-------------|
| `actions` | No | List of actions to execute |
| `next_step` | No | Step ID to jump to after this branch |

**next_step priority** (highest to lowest):
1. Branch-level `then.next_step` or `else.next_step`
2. Step-level `next_step`
3. Sequential (next step in flow order)

**Key Features**:

- All conditions use Jinja2 template syntax for dynamic evaluation
- Branches can route to different steps, enabling efficient skip-ahead patterns
- Steps with no meaningful condition that just run actions should use `type: action` instead

#### `action`

Runs a list of actions and proceeds to the next step. No branching, no termination — a pure side-effect step.

Use this instead of `conditional_branch` with `if: "{{ true }}"` when you only need to execute actions without a condition.

```yaml
- id: init_gold
  type: action
  actions:
    - set_value:
        path: "variables.gold"
        value: "{{ inputs.current_gold | int }}"
    - set_value:
        path: "outputs.remaining_gold"
        value: "{{ inputs.current_gold | int }}"
  next_step: shop_menu

- id: record_purchase
  type: action
  actions:
    - append_value:
        path: "outputs.purchased_items"
        value: "{{ variables.last_item_id }}"
    - display_message: "✅ Purchased {{ variables.last_item_name }}."
  next_step: prompt_equip
```

#### `flow_call`

Invokes another flow as a sub-flow. The sub-flow's outputs are available as `result` in subsequent actions.

```yaml
- id: call_character_creation
  type: flow_call
  flow: generate_character_name
  inputs:
    character: "{{ variables.character_without_name }}"
  actions:
    # for this step, result is the "outputs" of the sub-flow
    - set_value:
        path: "variables.character.name"
        value: "result.character.name"
```

## Actions

Actions are operations performed during step execution. All actions use generic reference-based operations to maintain system agnosticism.

### Core Actions

#### `set_value`

Sets a value at a reference path.

```yaml
- set_value:
    path: "outputs.character.level"
    value: 1
```

#### `swap_values`

Swaps values between two reference paths.

```yaml
- swap_values:
    path1: "outputs.character.abilities.strength.bonus"
    path2: "outputs.character.abilities.dexterity.bonus"
```

#### `display_value`

Displays a model or object to the user.

```yaml
- display_value: "outputs.character"
```

#### `display_message`

Display a simple message to the user to be output with the information about the flow's execution. Supports templating. Also supports passing the message template as a string or dict.

```yaml
# Passing as a dict
- display_message:
    message: "{{ item|title }}: {{ result.total }} ({{ result.detail }})"

# Shorthand: passing as a string
- display_message: "{{ item|title }}: {{ result.total }} ({{ result.detail }})"
```

#### `validate_value`

Validates a model or object.

```yaml
- validate_value: "outputs.character"
```

#### `flow_call`

Calls another flow as a sub-flow. This is a convenience to avoid always needing to define a full step for sub-flow invocation.

```yaml
- flow_call:
    flow: "add_item_to_character"
    inputs:
      character_ref: "outputs.character"
      item: "{{ selected_weapon }}"
```

#### `log_event`

Logs an event for debugging or analytics.

```yaml
- log_event:
    type: "dice_rolled"
    data: "{{ result }}"
```

#### `log_message`

Logs a simple message for debugging or user information. Supports templating. Also supports passing the message template as a string or dict.

```yaml
# Passing as a dict
- log_message:
    message: "{{ item|title }}: {{ result.total }} ({{ result.detail }})"

# Shorthand: passing as a string
- log_message: "{{ item|title }}: {{ result.total }} ({{ result.detail }})"
```

## Templating

Flows use Jinja2 templating syntax for dynamic content:

- **Variables**: `{{ variables.hp_dice_roll }}`
- **References**: `{{ outputs.character.name }}`
- **Filters**: `{{ item|title }}`, `{{ value|upper }}`
- **Conditionals**: `{{ outputs.character.name || 'Unnamed Character' }}`

## Flow Control

### Step Transitions

Steps can specify their next step explicitly:

```yaml
next_step: "roll_damage"
```

Or rely on sequential execution (next step in the array).

### Conditional Execution

Steps can include conditions for execution:

```yaml
condition: "llm_enabled"
condition: "previous_choice == 'advanced_rules'"
```

### Parallel Execution

Steps can execute operations in parallel:

```yaml
parallel: true
```

This is particularly useful for:

- Multiple table rolls
- Independent dice rolls
- API calls (like LLM generation)

### Resume Points

Flows can be paused and resumed at designated points:

```yaml
resume_points: ["choose_weapon", "generate_traits", "review_character"]
```

## Design Principles

1. A flow should encapsulate a complete, discrete game mechanic (e.g., character creation, ability check).
1. When designing flows, think in terms of discrete steps that can be easily understood and executed.
1. When building complex flows, break them into smaller sub-flows that can be reused and tested in isolation.
1. Use actions to encapsulate common operations and maintain system agnosticism.

## Example: Complete Character Creation Flow for Knave 1st Edition

A complete character creation flow for the Knave 1st Edition RPG system is provided in the [systems/knave_1e/flows/character_creation.yaml](../systems/knave_1e/flows/character_creation.yaml) file. This flow demonstrates the use of various step types, actions, and flow control mechanisms to guide a player through creating a character, including rolling abilities, selecting equipment, and finalizing the character sheet.

This specification provides a robust foundation for defining tabletop RPG rules as executable flows while maintaining flexibility and reusability across different game systems.
