# Roadmap Addendum — Custom GPT to Plugin Migration

Date: 2026-09-16

This addendum supersedes the assumption that Phase 10 Custom GPT integration is the permanent product surface.

## Phase 10 status reinterpretation

Phase 10 remains **technically complete and accepted** for the current Custom GPT compatibility period:

- read-only HTTPS backend works;
- eight canonical operations work;
- auth/privacy/public HTTPS acceptance passed;
- current K-Trader GPT remains usable while supported by ChatGPT.

However, Custom GPT is now classified as **legacy product integration** because OpenAI announced planned retirement and migration to Plugins.

## New Phase 10P — Plugin Migration

Status: **PREPARATION ACTIVE / ACTIVATION PENDING PLATFORM AVAILABILITY**

Objectives:

1. Extract durable K-Trader workflow into a reusable skill.
2. Preserve the canonical read-only backend as an integration-neutral service.
3. Replace legacy Custom Action attachment with a supported Plugin app/connector/MCP integration.
4. Preserve authentication, permissions and read-only safety.
5. Build and execute migration regression tests.
6. Re-establish sharing/access independently of the old GPT.
7. Keep the current Custom GPT operational until replacement acceptance.

Prepared artifacts:

- `docs/plugin_migration/README.md`;
- `docs/plugin_migration/K_TRADER_SKILL_DRAFT.md`;
- `docs/plugin_migration/INTEGRATION_CONTRACT_V1.md`;
- `docs/plugin_migration/REGRESSION_SUITE.md`;
- `custom_gpt/LEGACY_MIGRATION_NOTICE_2026-09-16.md`.

## Phase 10P exit criteria

- migration/plugin creation flow available to the relevant account/workspace;
- K-Trader skill created from the accepted draft;
- read-only integration connected;
- eight canonical capabilities available or equivalently mapped;
- auth/permission tests PASS;
- semantic regression suite PASS;
- replacement Plugin access/sharing verified;
- legacy Custom GPT retirement/fallback plan documented;
- explicit acceptance checkpoint created.

## Relationship to Phase 11G

Phase 10P product migration and Phase 11G strategy evidence collection are independent workstreams.

Plugin migration must not alter:

- frozen v2.2;
- prospective evidence;
- resolver semantics;
- holdout state;
- production trading authorization.

Phase 11G can continue while Phase 10P is prepared.
