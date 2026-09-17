# K_AI -> K-Trader Live E2E Preflight — 2026-09-17

Status: `BLOCKED_TRANSPORT` — adapter contract ready; live producer transport endpoint is not yet reachable/configured from K-Trader.

## Scope

This preflight covers the read-only integration path:

`MT4 -> K_AI MARKET_CONTEXT schema 1.1 -> private transport -> K-Trader KAIMT4MarketContextAdapter`

It does not authorize provider activation, strategy/risk/execution changes, holdout access, broker actions or trading.

## Producer source verified

K_AI repository: `kolemasakar/K_AI-Trading-System`

Authoritative source for this upgrade:

- branch `feature/native-m15-market-context-1.1`;
- architecture review `b04ef2439fec48f13f85e3a056228f6614bb1f22`;
- implementation `4ac4e5d5e3b35d6fb0dc2dda252e1b8eb0241b72`.

The feature branch currently points to the implementation commit above. Its canonical contract is schema `1.1`, exact scopes `D1/H1/M15/M5`, native MT4 `PERIOD_M15`, depths `D1=60/H1=200/M15=300/M5=300`, `time_source=BrokerServer`, `timestamp_semantics=BROKER_SERVER_WALL_CLOCK_OPAQUE`, and `utc_offset_minutes=null`.

Producer-side live validation already recorded run `M15LIVE_20260917_135101_433422`, `ETHUSDt`, imported native M15 depth/count `300`, strict chronology and no broker execution.

## K-Trader consumer readiness

Draft PR `#60`, branch `integration/kai-mt4-market-context`, contains an inactive-by-default adapter with fail-closed validation for:

- schema 1.0 when `require_m15=True`;
- wrong exact scope set;
- canonical bar-depth mismatch;
- wrong/missing opaque timestamp semantics;
- non-null/fabricated UTC offset semantics;
- duplicate/non-chronological source timestamps;
- current bar not after latest closed bar;
- malformed/non-finite market facts and OHLCV;
- invalid OHLC and negative volume.

A repeatable live acceptance runner is available at `scripts/kai_mt4_e2e_acceptance.py`. It emits a redacted machine-readable result and does not expose bearer tokens.

## Transport preflight result

Checked from production host `k-trader-prod-vnic`:

- no `KAI_MT4_BASE_URL` in host environment;
- no `KAI_MT4_API_TOKEN` in host/container environment;
- no local listener on TCP `8765`;
- no K_AI/HP-OMEN endpoint alias in `/etc/hosts`;
- no K_AI transport settings in `/opt/k-trader/runner/.env` or `env.sh`;
- K_AI authoritative feature tree does not contain an HTTP service implementing `POST /v1/market-context/acquire`.

Therefore a real network `K_AI -> K-Trader` E2E request cannot currently be executed from K-Trader. Static payload replay is not accepted as a substitute for live E2E.

## Required condition to unblock

Provide a private K_AI transport surface reachable from `k-trader-prod-vnic` that implements the agreed read-only endpoint:

`POST /v1/market-context/acquire`

The K-Trader runtime then needs only:

- `KAI_MT4_BASE_URL=<private endpoint>`;
- `KAI_MT4_API_TOKEN` only if bearer authentication is enabled.

No Remote Desktop or access to `D:\_AI_Trading_System` is required by K-Trader.

## Acceptance command after transport exists

```bash
python scripts/kai_mt4_e2e_acceptance.py \
  --symbol ETHUSDt \
  --market crypto \
  --negative-contract-smoke \
  --output reports/audits/kai_mt4_e2e_acceptance.json
```

PASS requires a fresh live schema 1.1 response accepted by the adapter plus all local negative contract cases failing closed. Provider registry and production activation remain unchanged after acceptance.
