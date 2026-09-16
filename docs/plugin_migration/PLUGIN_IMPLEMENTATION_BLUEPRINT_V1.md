# K-Trader Plugin Implementation Blueprint v1

Status: **MIGRATION-READY DESIGN / NO CUTOVER AUTHORIZED**

Verified against OpenAI public guidance on 2026-09-16.

## Product direction

OpenAI is moving Custom GPT workflows toward Plugins. Durable workflow behavior should live in skills; external data/tools should be exposed through connected apps/integrations, with custom integrations built around MCP where appropriate.

Custom GPT Actions do not transfer automatically through the migration flow.

Therefore K-Trader must treat the current GPT Builder + OpenAPI Action as a compatibility wrapper, not the long-term product boundary.

## Target composition

```text
K-Trader Plugin
├── K-Trader Skill
│   ├── workflow instructions
│   ├── safety/authority boundaries
│   ├── canonical-vs-fallback behavior
│   ├── output contract
│   └── examples/regression cases
└── K-Trader App / Integration
    └── thin MCP-based adapter when a custom integration is required
        └── existing K-Trader read-only HTTPS backend
```

No trading logic should be duplicated in the Plugin adapter.

## Component A — Skill

Current source baseline:

`docs/plugin_migration/K_TRADER_SKILL_DRAFT.md`

The skill owns reusable workflow guidance only:

- Ukrainian-first response behavior;
- canonical data priority;
- `NO TRADE` / `WATCHLIST ONLY` semantics;
- provider/market-type integrity;
- closed-bar/no-lookahead rules;
- research governance;
- portfolio-risk interpretation;
- output formatting and uncertainty handling.

The skill must not contain:

- API secrets;
- exchange credentials;
- environment-specific host secrets;
- mutable production state;
- provider-specific order execution logic.

## Component B — Connected app / MCP adapter

Preferred responsibility:

- authenticate to the K-Trader backend using the platform-supported integration mechanism;
- expose the eight existing read-only canonical capabilities as typed tools;
- preserve server-side semantics and structured errors;
- add no local trading decisions.

Required tool semantics:

| Capability | Canonical backend operation |
|---|---|
| health | `getHealth` |
| scanner status | `getScannerStatus` |
| universe | `listUniverse` |
| market snapshot | `getMarketSnapshot` |
| candles | `getCandles` |
| analysis | `getAnalysis` |
| candidates | `listCandidates` |
| signals | `listSignals` |

The adapter may rename tool identifiers if required by the Plugin/App/MCP platform, but meaning and validation must remain equivalent.

## MCP design constraints

If a custom MCP server is required:

- expose read-only tools only;
- no order/create/update/delete capability;
- no exchange-account tool;
- no generic HTTP proxy tool;
- no arbitrary filesystem/shell tool;
- bounded list/candle limits;
- provider ambiguity remains a structured failure;
- freshness/readiness remains backend-owned;
- backend error status must not be rewritten into successful trade advice;
- service credentials remain server-side and rotatable.

## Authentication transition

Legacy path:

`Custom GPT Action -> Bearer KTRADER_ACTION_API_KEY -> backend`

Target path:

`Plugin/App authorization -> integration/MCP service -> backend`

The migration must not assume the legacy ChatGPT-facing bearer secret is the correct long-term mechanism.

No secret is stored in the skill.

## Permissions target

Least-privilege scope:

- read K-Trader health/status;
- read universe/market/candles;
- read canonical analysis/candidates/signals;
- no unrelated user-data access;
- no exchange-account access;
- no write/trading permission.

The replacement Plugin begins as a private/test deployment until all regression gates pass and sharing is explicitly reviewed.

## Migration package contents

The repository-side migration package consists of:

- `K_TRADER_SKILL_DRAFT.md` — durable behavior;
- `INTEGRATION_CONTRACT_V1.md` — backend/tool semantics;
- `REGRESSION_SUITE.md` — product behavior tests;
- `SOURCE_ASSESSMENT_2026-09-16.md` — source verification;
- this implementation blueprint;
- legacy `custom_gpt/*` retained for compatibility/audit until retirement/cutover.

## Packaging caution

Do not invent or freeze a repository manifest format before the migration experience / current Plugin developer surface exposes the exact required packaging contract for this account/workspace.

Repository preparation should remain implementation-ready but packaging-neutral until that contract is observable.

## Acceptance sequence

1. Migration/create replacement Plugin when available for the account.
2. Import/recreate the K-Trader skill from the durable skill source.
3. Rebuild the external integration using a supported App/connector/MCP path.
4. Configure least-privilege authentication.
5. Confirm all eight canonical capabilities.
6. Run regression suite against the legacy GPT and replacement Plugin.
7. Verify hard cases: empty signals, degraded scanner, stale/missing history, provider ambiguity, invalid auth, unsupported intervals.
8. Verify no write/trading tool exists.
9. Review sharing/access explicitly; do not assume GPT sharing transfers.
10. Only after acceptance, designate the Plugin as the primary ChatGPT product surface.

## Cutover gate

Cutover is forbidden until all are true:

- skill selection/behavior acceptance PASS;
- integration acceptance PASS;
- auth/permission acceptance PASS;
- regression parity PASS for safety-critical behavior;
- access/sharing reviewed;
- recovery/rollback path documented;
- legacy GPT remains available until the cutover decision unless platform retirement forces removal.

## What does not change

Plugin migration does not change:

- production trading authorization;
- frozen strategy v2.2;
- Phase 11G evidence rules;
- provider semantics;
- risk rules;
- backend authority;
- `K_Investigation_Forecast` responsibility boundary.
