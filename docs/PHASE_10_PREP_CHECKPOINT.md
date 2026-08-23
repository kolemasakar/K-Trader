# Phase 10 Preparation Checkpoint

Date: 2026-08-23

Status: REPOSITORY-SIDE PREPARATION VERIFIED / LIVE ACTIVATION BLOCKED BY REAL HTTPS HOST.

## Prepared repository-side

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

## Verification evidence

PR #4 (`Phase 10 prep + Phase 11A replay regression hardening`) passed GitHub Actions CI run:

`32647828382`

Integrated result:

- Python compile: PASS;
- shell syntax validation: PASS;
- repository-wide pytest: **106 passed, 1 dependency deprecation warning**;
- linux/amd64 Docker build/runtime import: PASS;
- linux/arm64 QEMU/Buildx build: PASS;
- ARM64 architecture assertion: PASS;
- ARM64 production ASGI import: PASS;
- packaged target-host acceptance utility on both architectures: PASS.

PR #4 was squash-merged to `main` as:

`a1c578524bbc41afa575b3f4fb6446642a48453d`

## OpenAI product assumptions

Current OpenAI documentation was re-checked on 2026-08-23 before this preparation: Actions use external APIs defined by OpenAPI plus configured authentication; API-key Bearer auth is supported; GPTs cannot use Apps and Actions simultaneously; Actions are unavailable in Pro mode; public/shared GPTs with Actions require a valid Privacy Policy URL.

These product rules are external and must be re-checked immediately before activation.

## Remaining live activation gate

Phase 10 activation remains pending until Oracle or another approved host provides real HTTPS and Phase 9 live acceptance passes.

At that point:

1. create a high-entropy `KTRADER_ACTION_API_KEY` and store it only in the GitHub `production` Environment and GPT Action authentication;
2. render `custom_gpt/openapi.yaml` with the real HTTPS origin;
3. run `scripts/phase10_action_acceptance.py` against the deployed host;
4. configure the existing K_Trader GPT Action using `custom_gpt/BUILDER_CHECKLIST.md`;
5. verify source/freshness/provider ambiguity/NO_TRADE behavior in Preview;
6. add the deployed `/privacy` URL if the publishing mode requires it.
