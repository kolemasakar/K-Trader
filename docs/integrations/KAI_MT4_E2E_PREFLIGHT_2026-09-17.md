# K_AI -> K-Trader Live E2E Preflight — 2026-09-17

Status: `TRANSPORT_REACHABLE_AUTH_REQUIRED` — bounded delivery is live on K-Trader loopback; authenticated acquisition still requires the out-of-band bearer credential.

## Scope

This preflight covers:

`MT4 -> K_AI MARKET_CONTEXT schema 1.1 -> bounded loopback HTTP over restricted reverse SSH -> K-Trader validator`

It does not authorize provider activation, strategy/risk/execution changes, holdout access, broker actions or trading.

## Producer source verified

K_AI repository: `kolemasakar/K_AI-Trading-System`.

Per owner instruction, the native-M15 implementation remains verified from:

- branch `feature/native-m15-market-context-1.1`;
- architecture review `b04ef2439fec48f13f85e3a056228f6614bb1f22`;
- implementation `4ac4e5d5e3b35d6fb0dc2dda252e1b8eb0241b72`.

Its canonical contract is schema `1.1`, exact scopes `D1/H1/M15/M5`, native MT4 `PERIOD_M15`, depths `D1=60/H1=200/M15=300/M5=300`, `time_source=BrokerServer`, `timestamp_semantics=BROKER_SERVER_WALL_CLOCK_OPAQUE`, and `utc_offset_minutes=null`.

Producer-side native-M15 live validation recorded run `M15LIVE_20260917_135101_433422`, `ETHUSDt`, imported native M15 depth/count `300`, strict chronology and no broker execution.

## Delivery implementation verified

The bounded K_AI delivery layer was added and accepted separately from the native-M15 implementation:

- architecture boundary commit `3e7895e9e74f0f4f9728e92d35ad6b26626a344f`;
- delivery implementation commit `160713e3bdf31010b994a8e515e58820d58b8c90`;
- delivery acceptance/documentation commit `1c3c9e4eaf0611e28ac4e8ee430e05c19413c13e`.

Producer contract:

- K_AI listener: loopback `127.0.0.1:8765`;
- K-Trader-side restricted reverse-SSH listener: `127.0.0.1:18765`;
- health: `GET /health`;
- acquisition: `POST /v1/market-context/acquire`;
- authentication: HTTP Bearer token sourced from runtime `KAI_MARKET_CONTEXT_DELIVERY_TOKEN`;
- only canonical immutable `MARKET_CONTEXT` is returned;
- no generic RPC, filesystem, strategy, risk or execution/action surface is exposed.

K_AI delivery acceptance recorded live run `MCTXDELIVERY_20260917_145924_216739_A76C89D6` with schema `1.1`, source `MT4`, exact scopes `D1/H1/M15/M5`, depths `60/200/300/300`, valid opaque BrokerServer timestamps, zero strategy/execution side effects and no `signal.json`.

## K-Trader consumer readiness

Draft PR `#60`, branch `integration/kai-mt4-market-context`, contains an inactive-by-default consumer adapter with fail-closed validation for:

- schema 1.0 when `require_m15=True`;
- wrong exact scope set;
- canonical bar-depth mismatch;
- missing scope snapshot IDs;
- wrong/missing opaque timestamp semantics;
- non-null/fabricated UTC offset semantics;
- duplicate/non-chronological source timestamps;
- current bar not after latest closed bar;
- malformed/non-finite market facts and OHLCV;
- invalid OHLC and negative volume.

`scripts/kai_mt4_http_e2e.py` performs the bounded HTTP acquisition and then passes the returned payload into the transport-neutral adapter. The bearer secret is read only from environment variable `KAI_MARKET_CONTEXT_DELIVERY_TOKEN`; the runner does not accept the token as a command-line argument and does not print it.

## K-Trader host preflight result

Verified from `k-trader-prod-vnic`:

- TCP listener `127.0.0.1:18765` is active;
- `GET http://127.0.0.1:18765/health` returns HTTP `200` and `execution_surface=false`;
- `/` returns `404`;
- unauthenticated `POST /v1/market-context/acquire` returns `401 UNAUTHORIZED`, confirming bearer enforcement;
- no provider registration or production activation was performed.

The transport blocker is closed. The remaining live-E2E prerequisite is only the out-of-band consumer bearer credential matching the K_AI runtime `KAI_MARKET_CONTEXT_DELIVERY_TOKEN`.

## Authenticated acceptance command

After the credential is provisioned into the execution environment:

```bash
export KAI_MARKET_CONTEXT_DELIVERY_TOKEN='<out-of-band secret>'
python scripts/kai_mt4_http_e2e.py \
  --symbol ETHUSDt \
  --market crypto \
  --negative-contract-smoke \
  --output reports/audits/kai_mt4_http_e2e_acceptance.json \
  --save-payload reports/audits/kai_mt4_http_e2e_payload.json
```

PASS requires a fresh authenticated schema 1.1 response from K_AI accepted unchanged by K-Trader plus all local negative contract cases failing closed. Provider registry and production activation remain unchanged after acceptance.
