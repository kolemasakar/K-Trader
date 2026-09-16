# K-Trader Plugin Migration

Status: **PREPARATION ACTIVE / CUSTOM GPT LEGACY WRAPPER STILL SUPPORTED**

Date: 2026-09-16

## Trigger

OpenAI announced planned retirement of Custom GPTs and migration toward Plugins. Plugins combine reusable skills with apps/integrations. Custom Actions are not assumed to migrate automatically.

For K-Trader this changes the product integration layer, not the canonical market/research backend.

## Architectural decision

Long-term target:

`K-Trader Plugin = K-Trader Skill + read-only K-Trader App/Connector integration`

If the supported custom-integration path requires it, use a thin MCP adapter between the Plugin/App surface and the existing backend.

The current Custom GPT remains a temporary compatibility wrapper until replacement acceptance.

The existing production backend remains integration-neutral and read-only:

- `/health`;
- `/v1/scanner/status`;
- `/v1/universe`;
- `/v1/market/{symbol}`;
- `/v1/candles/{symbol}`;
- `/v1/analysis/{symbol}`;
- `/v1/candidates`;
- `/v1/signals`.

No order/account endpoint is introduced by this migration.

## What is preserved

- K-Trader analytical behavior and safety rules;
- canonical server-decision priority;
- Ukrainian response policy;
- read-only boundary;
- provider/freshness/provenance semantics;
- strategy/research governance;
- backend API and production data model;
- regression behavior for `NO TRADE`, `WATCHLIST ONLY`, ambiguity and missing-data cases.

## What changes

### Legacy

- `custom_gpt/SYSTEM_*` as GPT Builder instructions;
- `custom_gpt/openapi.yaml` as a Custom Action attachment;
- Builder-specific publishing/checklist flow.

These remain available until migration is complete and verified.

### Target

- behavioral instructions become a reusable K-Trader skill;
- backend access becomes an app/connector/MCP-based integration supported by the Plugin environment;
- Plugin permissions/sharing are configured independently;
- migration validation uses a dedicated regression suite.

## Migration rules

1. Do not delete or disable the current working Custom GPT before replacement acceptance.
2. Do not assume Custom Actions migrate automatically.
3. Do not expose production secrets in skill/reference files.
4. Keep backend auth and authorization independent of ChatGPT conversation instructions.
5. Preserve read-only API semantics during migration.
6. Treat the replacement Plugin as private until regression and access tests pass.
7. Re-test permissions/sharing after migration; old GPT access does not imply Plugin access.
8. Do not tie K-Trader business logic to a selected ChatGPT model.
9. Do not invent/freeze a final Plugin package manifest until the actual migration/developer surface for the account exposes its current required contract.

## Prepared artifacts

- `K_TRADER_SKILL_DRAFT.md` — migration-ready behavioral specification;
- `INTEGRATION_CONTRACT_V1.md` — app/connector/MCP requirements;
- `REGRESSION_SUITE.md` — acceptance scenarios;
- `SOURCE_ASSESSMENT_2026-09-16.md` — verified product-change assessment;
- `PLUGIN_IMPLEMENTATION_BLUEPRINT_V1.md` — target composition, permissions, MCP/app constraints, cutover sequence;
- `../operations/PRODUCTION_SAFETY_EXECUTION_COMPATIBILITY_AUDIT_2026-09-16.md` — current backend safety baseline.

## Activation gate

Plugin migration becomes operational only after the migration/plugin creation experience is available for the account/workspace and the following pass:

- skill behavior regression;
- app/integration connectivity;
- authentication and permissions;
- all canonical read-only operations;
- fallback behavior;
- privacy/access review;
- end-user installation/access test.

Until then the existing Custom GPT integration remains supported but is classified as **legacy/temporary**.
