# K-Trader — OpenAI Custom GPT → Plugin transition

Date: 2026-09-16  
Status: **STRATEGIC REBASE / NO RUNTIME MUTATION**

## Why this exists

OpenAI has announced retirement of Custom GPTs and migration toward Plugins. For K-Trader this matters directly because the repository contains a `custom_gpt/` deployment package with Builder instructions/checklist and an OpenAPI Action schema.

This document changes the strategic target without changing live K-Trader runtime, trading rules, production deployment, or current research execution.

## Current legacy assets

Treat the existing `custom_gpt/` package as a migration source package, not the long-term product surface:

- `custom_gpt/SYSTEM_K_TRADER_v1_3_COMPACT.md` and earlier instruction variants → source for future Plugin skill/workflow;
- `custom_gpt/openapi.yaml` → source specification for future App/Connector/MCP integration;
- `custom_gpt/ACTION_GUIDE.md` → migration input for integration behavior and auth boundaries;
- `custom_gpt/BUILDER_CHECKLIST.md` → legacy deployment checklist retained for audit/short-term maintenance only;
- knowledge/reference files → preserve as structured reference assets.

## New target architecture

```text
PRIMARY_PRODUCT_TARGET = K-Trader Plugin
LEGACY_DEPLOYMENT       = existing Custom GPT until retirement

Custom GPT Instructions
-> Plugin Skill / workflow

Custom GPT OpenAPI Action
-> supported App / Connector / custom MCP integration

GPT Builder regression
-> Plugin regression / acceptance suite
```

## Migration principles

- Do not delete or rewrite the current Custom GPT package while the legacy GPT remains usable.
- Do not assume OpenAPI Custom Actions migrate automatically.
- Preserve instruction semantics, trading-risk gates, output contracts, and backend API contracts as explicit migration requirements.
- Decouple business logic from a selected ChatGPT model or GPT-specific UX.
- Build regression tests from current K-Trader GPT scenarios before changing the deployment surface.
- Any Plugin publication/sharing remains a separate owner authorization gate.
- No production runtime, server, trading algorithm, dataset, or execution authority is changed by this document.

## Workstream

1. Inventory current Custom GPT instructions, knowledge, Actions/auth and conversation-start UX.
2. Extract canonical K-Trader skill/workflow from `SYSTEM_K_TRADER_v1_3_COMPACT.md`.
3. Map `custom_gpt/openapi.yaml` operations to supported Plugin integration primitives.
4. Preserve backend API as-is where feasible; change the ChatGPT-facing integration layer only where required.
5. Build regression suite for current K-Trader behavior.
6. Create private Plugin candidate.
7. Run parallel GPT-vs-Plugin validation.
8. Configure sharing/publication only after separate approval.

## Current priority effect

The Custom GPT Builder is no longer a strategic endpoint. Builder-specific work is allowed only when needed to keep the current K-Trader GPT operational during the transition. New substantial product work should target Plugin-compatible skill/integration architecture.

## Boundaries

```text
KTRADER_RUNTIME_CHANGE=NONE
TRADING_LOGIC_CHANGE=NONE
PRODUCTION_DEPLOYMENT_CHANGE=NONE
CUSTOM_GPT_DELETION=DENIED
PLUGIN_PUBLICATION=HOLD
```

Source context: `kolemasakar/AI_general/docs/openai-custom-gpts-retirement-to-plugins-2026-09-16.md`.
