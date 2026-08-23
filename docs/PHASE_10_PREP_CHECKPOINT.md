# Phase 10 Preparation Checkpoint

Date: 2026-08-23

Status: IMPLEMENTED / PR CI VERIFICATION PENDING / LIVE ACTIVATION BLOCKED BY HTTPS HOST.

Prepared repository-side:

- precise read-only OpenAPI response schemas;
- Bearer API-key security scheme;
- optional server enforcement via `KTRADER_ACTION_API_KEY` on `/v1/*`;
- public `/health` and `/privacy` endpoints;
- production GitHub Environment secret wiring;
- schema render/validation utility;
- live Action acceptance utility;
- Builder checklist;
- repository privacy-policy baseline;
- tests for schema YAML validity, read-only methods, required operation IDs, HTTPS origin validation, Bearer protection, and hidden privacy endpoint.

Current OpenAI documentation was re-checked on 2026-08-23 before this preparation: Actions use external APIs defined by OpenAPI plus configured authentication; API-key Bearer auth is supported; GPTs cannot use Apps and Actions simultaneously; Actions are unavailable in Pro mode; public GPTs with Actions require a valid Privacy Policy URL. Re-check at live activation.

Phase 10 activation remains pending until Oracle/other approved host provides real HTTPS and Phase 9 live acceptance passes.
