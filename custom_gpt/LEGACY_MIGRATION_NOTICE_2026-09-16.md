# Custom GPT Legacy Migration Notice — 2026-09-16

Status: **LEGACY COMPATIBILITY PATH / STILL ACTIVE UNTIL REPLACEMENT ACCEPTANCE**

OpenAI has announced planned retirement of Custom GPTs and migration toward Plugins.

Therefore the contents of `custom_gpt/` remain operational documentation for the currently working K-Trader Custom GPT, but they are no longer the long-term product architecture.

In particular:

- `SYSTEM_K_TRADER_v1_3_COMPACT.md` is the current behavioral source used to prepare a migration-ready skill;
- `openapi.yaml` is a legacy Custom Action transport schema;
- `ACTION_GUIDE.md` and `BUILDER_CHECKLIST.md` remain useful for current compatibility but should not be expanded as the future integration design;
- Custom Actions are not assumed to migrate automatically.

Target migration documentation lives under:

`docs/plugin_migration/`

Do **not** remove or disable the current Custom GPT before the replacement Plugin passes skill/integration/auth/sharing regression and is explicitly accepted.

The canonical K-Trader backend remains read-only and is intended to survive the product-layer migration unchanged where possible.
