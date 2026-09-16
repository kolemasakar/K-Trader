# K-Trader Plugin Integration Contract v1

Status: **MIGRATION PREPARATION / READ-ONLY**

## Goal

Define how a future K-Trader Plugin app/connector/MCP integration should expose the existing canonical backend without importing legacy Custom GPT assumptions into the backend itself.

## Backend remains authoritative

Existing HTTPS backend:

`https://ktrader-api.duckdns.org`

Canonical read-only capabilities:

| Capability | Current operation |
|---|---|
| health | `getHealth` |
| scanner status | `getScannerStatus` |
| universe | `listUniverse` |
| market snapshot | `getMarketSnapshot` |
| candles | `getCandles` |
| analysis | `getAnalysis` |
| candidates | `listCandidates` |
| signals | `listSignals` |

The Plugin integration may rename or wrap these calls to fit the supported app/MCP interface, but semantics must remain equivalent and versioned.

## Mandatory properties

- read-only operations only;
- no exchange account endpoints;
- no order create/modify/cancel endpoints;
- no exchange credentials in skill/reference assets;
- explicit auth handled by the app/connector, not by natural-language instructions;
- provider ambiguity remains fail-closed;
- freshness/history readiness remain server-side/canonical facts;
- structured errors must preserve enough information for safe fallback behavior;
- API/backend version must be observable.

## Auth

Current legacy Action uses Bearer authentication protected by `KTRADER_ACTION_API_KEY`.

Migration must not assume this exact ChatGPT-facing auth mechanism remains appropriate. The replacement integration should use the authentication method supported by the selected Plugin app/connector/MCP path while keeping secrets outside the skill.

The backend may retain a service credential if needed, but credential rotation and storage must remain infrastructure concerns.

## Permissions

Required Plugin/app permission profile:

- read K-Trader market/scanner/analysis data;
- no write/trading permission;
- no access to exchange accounts;
- no access to unrelated user data.

If the Plugin platform exposes action approval levels, all K-Trader v1 capabilities should remain in the low-risk read-only class.

## Expected integration mapping

Preferred target architecture:

`K-Trader Skill -> K-Trader App/Connector -> HTTPS read-only backend`

Alternative if direct app integration is not available:

`K-Trader Skill -> custom MCP server -> HTTPS read-only backend`

The MCP layer, if used, should be a thin typed adapter. It must not duplicate trading logic already owned by K-Trader.

## Typed interface requirements

Each tool/capability should expose:

- stable name/description;
- structured parameters;
- structured response;
- provider and symbol identifiers where relevant;
- UTC/as-of timestamps;
- freshness/status fields;
- bounded limits for list/candle operations.

The adapter should not silently convert provider ambiguity, missing history or degraded readiness into successful trade advice.

## Migration acceptance

Replacement integration passes only if:

- all eight canonical capabilities are callable;
- health/status semantics match current backend;
- invalid auth is rejected;
- unsupported interval/grade is rejected;
- ambiguous symbol behavior remains fail-closed;
- no write operation is exposed;
- Plugin skill can distinguish `NO TRADE` from integration failure;
- fallback mode activates only when canonical data are actually insufficient.

## Legacy boundary

`custom_gpt/openapi.yaml` and `ktrader.action_package` remain supported only for the existing Custom GPT compatibility path.

They are not the target Plugin integration contract and should not constrain the future app/MCP surface beyond preserving the same canonical backend semantics.
