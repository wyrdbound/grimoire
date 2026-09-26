# Changelog

## [1.2.0](https://github.com/wyrdbound/grimoire/compare/grimoire-spec-v1.1.1...grimoire-spec-v1.2.0) (2026-09-26)


### Features

* **knave:** complete roll_starting_gear for re-enabling ([38088de](https://github.com/wyrdbound/grimoire/commit/38088de6937776fd342451d26683dab5a430ac12))


### Bug Fixes

* **knave:** stop add_items_to_character shadowing inputs and truncating ([1ff9190](https://github.com/wyrdbound/grimoire/commit/1ff91905faf08354992499fb209de15a42680a04))
* **quickstart:** complete spell_slots defaults and store spells as a list ([d625c16](https://github.com/wyrdbound/grimoire/commit/d625c160286ca32534977e59b2d3b20f34d418b6))

## [1.1.1](https://github.com/wyrdbound/grimoire/compare/grimoire-spec-v1.1.0...grimoire-spec-v1.1.1) (2026-09-26)


### Bug Fixes

* **knave:** derive armor.defense from armor.bonus, not a bare bonus ([6f88a5d](https://github.com/wyrdbound/grimoire/commit/6f88a5de230b5079c648e1d7e18504e50fbe62d4))
* parse an output's `validate` flag ([c0aff71](https://github.com/wyrdbound/grimoire/commit/c0aff71a847403620a29eddc457363616e210c43))

## [1.1.0](https://github.com/wyrdbound/grimoire/compare/grimoire-spec-v1.0.0...grimoire-spec-v1.1.0) (2026-09-26)


### Features

* distinguish an explicit `default: null` from no default ([b82dd7f](https://github.com/wyrdbound/grimoire/commit/b82dd7f7038b2c7d6cf68b2b64e80ff3061a1c26))

## [1.0.0](https://github.com/wyrdbound/grimoire/compare/grimoire-spec-v0.1.1...grimoire-spec-v1.0.0) (2026-09-25)


### ⚠ BREAKING CHANGES

* `count` on a table_roll entry fails to load.
* a table with list entries must declare `multiple_entries: true`, and flows must read table results by the name the table's shape gives.
* a flow referencing an undefined `runtime.<name>` fails to load.
* a step `condition` that is not a `{{ }}` template fails to load.
* `optional` on a step other than player_choice fails to load.
* `result_message`, and `prompt` on completion steps, fail to load; flows using `choice`, `choice_entry`, `results` or `llm_result` must use `result`.
* a flow input declaring `required` fails to load.

### Features

* `multiple_entries` tables, with result shape checked at load ([8d7c9e4](https://github.com/wyrdbound/grimoire/commit/8d7c9e468498bd6ad175eb2f740456031501b20d))
* `optional: true` lets a player_choice be skipped ([021e838](https://github.com/wyrdbound/grimoire/commit/021e838c99b0307cb8fdf3cf42e72e2bcf02e7b9))
* `table_sequence` rolls one table N times; `count` leaves `table_roll` ([b4708bf](https://github.com/wyrdbound/grimoire/commit/b4708bf99f8ff84d5b6b2aa28821d77cc28248e8))
* a read-only `runtime` namespace; `runtime.llm_available` replaces `llm_enabled` ([583585b](https://github.com/wyrdbound/grimoire/commit/583585b0ece817a40df8f95bddd110754397857d))
* a step `condition` is a `{{ }}` template; false skips the step ([d2c307f](https://github.com/wyrdbound/grimoire/commit/d2c307f4b7764b2e9a21ab0a53b37393328f7ee3))
* flow inputs use `optional`, the same presence flag as model attributes ([55ac93c](https://github.com/wyrdbound/grimoire/commit/55ac93c15f0022c6962ca718cc3f44444ee62c70))
* one step output name (`result`) and `final_message` for completion ([891a98f](https://github.com/wyrdbound/grimoire/commit/891a98ffaba70bca7f692d67bcac1733a8126ae9))
* **spec:** a null table entry means "nothing"; Knave rolls no armour as null ([fedb367](https://github.com/wyrdbound/grimoire/commit/fedb367c34e237a0403586a1ca668412624ed332))


### Bug Fixes

* **knave:** bind llm_generation output as `result`, not `llm_result` ([e5ee21d](https://github.com/wyrdbound/grimoire/commit/e5ee21d53ac0de6b2d7b12d4e56c4f016fc190f9))
* **loader:** make `optional` the only presence flag and enforce the default rule ([9080eac](https://github.com/wyrdbound/grimoire/commit/9080eac3108f1e3c67142f9b45b9d94a5290c454))
* **loader:** validate table entries the way the table spec defines them ([513db0a](https://github.com/wyrdbound/grimoire/commit/513db0a334343de6d13cd5734aafffb04f9b1fe7))
* **quickstart:** equip the starting cloak in character creation, not by default ([03c3518](https://github.com/wyrdbound/grimoire/commit/03c35181b9f75c3ebb4d53800fb7e280e0df44a3))
* **quickstart:** mark the equipped slots optional instead of defaulting to null ([500f66a](https://github.com/wyrdbound/grimoire/commit/500f66a036834be9a358a1fc642d5dcea916086b))
* **quickstart:** tell mages they cannot wear armor instead of an empty table ([2687cf8](https://github.com/wyrdbound/grimoire/commit/2687cf807bcfd1bce32366507aac5779c027a178))
* **spec:** remove the `this.` prefix and `$` range form from model_spec ([3292761](https://github.com/wyrdbound/grimoire/commit/3292761a9eac24fa040c5314f0f1e09517fef490))
* **spec:** replace `&&`, `||` and `!` with Jinja2's `and`, `or`, `not` ([ff519d3](https://github.com/wyrdbound/grimoire/commit/ff519d337e10fe8c58d2fa67124c1b22bf8110e8))


### Documentation

* adopt the AGENTS.md convention ([046916c](https://github.com/wyrdbound/grimoire/commit/046916cd4f2d3b212e9febb8fd2ac7337fa7f3c7))
* **spec:** `parallel: true` applies results in declaration order ([3d8f47e](https://github.com/wyrdbound/grimoire/commit/3d8f47e513404bab67640f9729ce481c59b40e09))
* **spec:** define presence, defaults and null; document filters, not functions ([f9f7aee](https://github.com/wyrdbound/grimoire/commit/f9f7aeeea9d10c12da9f9eda8e63d47b872aeae9))
* **spec:** document the llm_generation `validation` block ([edfccdb](https://github.com/wyrdbound/grimoire/commit/edfccdb90a4be00ba68d62aa7d414df4d6ac5287))
* **spec:** state that `optional` is the only presence flag and defaults to false ([4b9ce56](https://github.com/wyrdbound/grimoire/commit/4b9ce562ade26d29c6936470e52e020b30f8b3fb))

## [0.1.1](https://github.com/wyrdbound/grimoire/compare/grimoire-spec-v0.1.0...grimoire-spec-v0.1.1) (2026-04-18)


### Bug Fixes

* publishing to PyPI ([7098477](https://github.com/wyrdbound/grimoire/commit/709847743b3291d2296a2d61b535848817ad526e))

## 0.1.0 (2026-04-18)


### Features

* add release-please and CI/CD workflows for PyPI publishing ([b4a7db5](https://github.com/wyrdbound/grimoire/commit/b4a7db50b891f8169f144247415d1e0433c2e85e))
* add release-please and CI/CD workflows for PyPI publishing ([d9fbb2b](https://github.com/wyrdbound/grimoire/commit/d9fbb2b0b2b6323d30fee372fb994365a8c761ec))
* add system loader with validation ([9c06637](https://github.com/wyrdbound/grimoire/commit/9c0663703003c3803142add229f8c8c209c2345d))
* character model equipped slots use model types; inventory tracks item IDs ([fbafdbc](https://github.com/wyrdbound/grimoire/commit/fbafdbcdcaa0b129bbaf5e5c1e931189305ea0ab))
* continuous equipment shop with category routing, afford check, and equip prompt ([225ee2f](https://github.com/wyrdbound/grimoire/commit/225ee2f7f6b867bba3df4615f10838e4096e3755))
* migrate calculate_starting_hp to structured then/else blocks with next_step ([479b45d](https://github.com/wyrdbound/grimoire/commit/479b45d9b8a988c2cedbecfd01bf01489762258d))
* **wq1e:** add default to determine_traits description output ([b85c1fa](https://github.com/wyrdbound/grimoire/commit/b85c1fad3b3490c8c65b18826fb9128fe63b8047))
* **wq1e:** add equipment system ([c9520d6](https://github.com/wyrdbound/grimoire/commit/c9520d614995e968f7b4c45b6ca33e3f6a028947))
* **wq1e:** add trait selection and character description to character creation ([3b9ebda](https://github.com/wyrdbound/grimoire/commit/3b9ebdacba3c3d36c941cdd11cec27195ddb9a27))
* **wq1e:** class-specific weapon/armor tables ([5bc6b9f](https://github.com/wyrdbound/grimoire/commit/5bc6b9fa3ad788d75745c4e3f38185691abbc8de))
* **wq1e:** dice details, confirm steps, LLM progress indicator ([038424f](https://github.com/wyrdbound/grimoire/commit/038424fb835bf7efbec600306b51a577745d189f))
* **wq1e:** move generate_description step to character_creation flow ([8ac36a7](https://github.com/wyrdbound/grimoire/commit/8ac36a70f7b0e11f1944af8da8f257131e2b9d1c))
* **wq1e:** replace physique/virtue/vice with bearing/manner/disposition ([f2f4e60](https://github.com/wyrdbound/grimoire/commit/f2f4e60a21fec890f0b8a23c6bc4e0f2b6b2f8a8))
* **wq1e:** use wyrdbound-dice description string for dice display ([138b383](https://github.com/wyrdbound/grimoire/commit/138b3832a4341cc2262312da9139f9015e98a8bd))
* **wyrdbound-quickstart-1e:** initial system spec ([e46ced7](https://github.com/wyrdbound/grimoire/commit/e46ced7b238ff558256a30e574a96671ec8d839b))


### Bug Fixes

* bug with wrong system name in load_system.py ([4516f52](https://github.com/wyrdbound/grimoire/commit/4516f5256cc4b69fb0b1cee6f08c7bde36fc360b))
* mypy failure ([ba1a610](https://github.com/wyrdbound/grimoire/commit/ba1a610ec95c16628784a68c6fbad664de7c48a9))
* permissions issue in release.yml ([88b1dff](https://github.com/wyrdbound/grimoire/commit/88b1dffb8377efe63c2ae30a1e63897195e96be7))
* remove manual modifier set_value steps from character_creation ([bc67df6](https://github.com/wyrdbound/grimoire/commit/bc67df6805015acb54cae5c80164ccd2d0f22220))
* silence warning with FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true ([#4](https://github.com/wyrdbound/grimoire/issues/4)) ([85065a0](https://github.com/wyrdbound/grimoire/commit/85065a0abed1f4ccca42f3ad0a2af9e3a7690fed))
* test failures ([e646fd1](https://github.com/wyrdbound/grimoire/commit/e646fd1408951d9ec235314fa95e427e9aa42166))
* **wq1e:** roll_attributes display uses description only (no redundant total) ([e787a18](https://github.com/wyrdbound/grimoire/commit/e787a18401923b8122b392ab80c7a03892c55d00))


### Documentation

* improve spec and Knave 1e reference implementation ([82b70e6](https://github.com/wyrdbound/grimoire/commit/82b70e6e37bbf31e2f09af163f008173546a5b50))
