# K_AI -> K-Trader Live E2E Preflight — 2026-09-17

Status: `BLOCKED_TRANSPORT` — adapter contract ready; cross-system read-only delivery from K_AI to K-Trader is not yet defined/deployed.

## Scope

This preflight covers:

`MT4 -> K_AI MARKET_CONTEXT schema 1.1 -> read-only delivery transport -> K-Trader KAIMT4MarketContextAdapter`

It does not authorize provider activation, strategy/risk/execution changes, holdout access, broker actions or trading.

## Producer source verified

K_AI repository: `kolemasakar/K_AI-Trading-System`.

Per owner instruction, the native-M15 implementation is verified from:

- branch `feature/native-m15-market-context-1.1`;
- architecture review `b04ef2439fec48f13f85e3a056228f6614bb1f22`;
- implementation `4ac4e5d5e3b35d6fb0dc2dda252e1b8eb0241b72`.

Its canonical contract is schema `1.1`, exact scopes `D1/H1/M15/M5`, native MT4 `PERIOD_M15`, depths `D1=60/H1=200/M15=300/M5=300`, `time_source=BrokerServer`, `timestamp_semantics=BROKER_SERVER_WALL_CLOCK_OPAQUE`, and `utc_offset_minutes=null`.

Producer-side live validation already recorded run `M15LIVE_20260917_135101_433422`, `ETHUSDt`, imported native M15 depth/count `300`, strict chronology and no broker execution.

## K-Trader consumer readiness

Draft PR `#60`, branch `integration/kai-mt4-market-context`, contains a transport-neutral, inactive-by-default consumer adapter with fail-closed validation for:

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

`scripts/kai_mt4_e2e_acceptance.py` accepts a freshly delivered canonical JSON payload from a file or stdin, validates it with `require_m15=True`, optionally executes local negative-contract smoke cases, and writes a machine-readable acceptance result. It deliberately does not define how K_AI delivers the payload.

## Transport preflight result

Checked from `k-trader-prod-vnic` and the authoritative K_AI feature tree:

- K-Trader has no configured K_AI cross-system transport;
- no K_AI endpoint/route/host alias is present in the current K-Trader deployment;
- K_AI native-M15 implementation uses its local file-bridge acquisition path;
- the authoritative K_AI tree does not establish a remote HTTP/MCP/other delivery service for K-Trader.

Therefore a real cross-system `K_AI -> K-Trader` E2E cannot currently be executed. Replaying the historical live-validation payload is useful for contract testing but is not accepted as a substitute for a fresh cross-system delivery.

## Required condition to unblock

Define and deploy one bounded, read-only delivery mechanism from K_AI to K-Trader. The transport may be HTTP, MCP, secure file delivery, or another explicitly accepted mechanism; the adapter itself remains transport-neutral.

Required properties:

- K-Trader receives the original canonical `MARKET_CONTEXT` JSON without timestamp reinterpretation or OHLC aggregation;
- authentication/authorization is bounded to market-context read/delivery only;
- no execution/risk/order surface is exposed;
- transport failure is fail-closed;
- a fresh payload can be tied to a K_AI `run_id` and producer evidence.

No Remote Desktop or direct K-Trader access to `D:\_AI_Trading_System` is required.

## Acceptance command after delivery exists

For a freshly delivered payload file:

```bash
python scripts/kai_mt4_e2e_acceptance.py \
  --input /path/to/fresh_market_context.json \
  --symbol ETHUSDt \
  --market crypto \
  --negative-contract-smoke \
  --output reports/audits/kai_mt4_e2e_acceptance.json
```

The same payload may be supplied on stdin if the chosen transport streams JSON.

PASS requires a fresh schema 1.1 payload from K_AI, accepted unchanged by K-Trader, plus all local negative contract cases failing closed. Provider registry and production activation remain unchanged after acceptance.
