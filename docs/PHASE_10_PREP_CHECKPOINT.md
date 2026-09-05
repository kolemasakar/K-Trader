# Phase 10 Preparation Checkpoint

Date: 2026-09-05

Status: REPOSITORY-SIDE PREPARATION VERIFIED / PHASE 9 PRODUCTION LIVE / PUBLIC HTTPS ACTIVATION PENDING.

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

## Repository verification evidence

PR #4 (`Phase 10 prep + Phase 11A replay regression hardening`) passed GitHub Actions CI run `32647828382`.

Integrated result:

- Python compile: PASS;
- shell syntax validation: PASS;
- repository-wide pytest: **106 passed**;
- linux/amd64 Docker build/runtime import: PASS;
- linux/arm64 QEMU/Buildx build: PASS;
- ARM64 architecture assertion: PASS;
- ARM64 production ASGI import: PASS;
- packaged target-host acceptance utility on both architectures: PASS;
- merge: `a1c578524bbc41afa575b3f4fb6446642a48453d`.

Later hardening remains compatible with this Phase 10 preparation. PR #17 final CI reached **170 tests PASS** with amd64/arm64 Docker gates passing.

## Phase 9 dependency resolved

The previous dependency on an approved live production host is now satisfied.

Verified on 2026-09-04:

```text
Oracle production VM: k-trader-prod
Architecture: aarch64
Allocation: 1 OCPU / 6 GB
Deployment run: 33920829993 -> SUCCESS
Deployed SHA: 9ed572349ed0195e518f128894a1f187419dbcc1
API bind: 127.0.0.1:8000
Health: status=ok, mode=read_only, data_ready=true
Docker: healthy
Provider: binance_usdm
Phase 9 REST/WS/MTF acceptance: PASS
```

Therefore Phase 10 is no longer blocked by Oracle capacity or Phase 9 live acceptance.

## OpenAI product assumptions

The original product assumptions were checked during repository preparation on 2026-08-23. Because GPT/Action product behavior can change, current OpenAI documentation must be re-checked immediately before live activation.

The repository must not treat the earlier product check as permanent evidence for current publishing or authentication rules.

## Remaining live activation gate

The remaining blocker is the real public HTTPS Action endpoint.

Required sequence:

1. choose the real API domain/subdomain;
2. create DNS A record to the production host public IPv4 `92.5.56.198`;
3. allow OCI inbound TCP 80 and 443;
4. create a high-entropy `KTRADER_ACTION_API_KEY` and store it only in the GitHub `production` Environment and GPT Action authentication;
5. set GitHub Environment variable `KTRADER_DOMAIN`;
6. redeploy approved `main`, enabling the Caddy HTTPS profile;
7. run/pass `scripts/phase10_action_acceptance.py` against the real HTTPS origin;
8. only after acceptance, render the deployment-specific OpenAPI schema with `scripts/render_custom_gpt_openapi.py`;
9. configure the existing K_Trader GPT Action using `custom_gpt/BUILDER_CHECKLIST.md`;
10. verify source/freshness/provider ambiguity/NO_TRADE behavior in Preview;
11. add the deployed `/privacy` URL if the selected publishing mode requires it.

Until step 7 passes, the canonical repository template `custom_gpt/openapi.yaml` must remain on `https://api.k-trader.invalid`.
