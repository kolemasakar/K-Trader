# K_AI MT4 live E2E acceptance — 2026-09-17

Status: `PASS` for bounded K_AI -> K-Trader MARKET_CONTEXT transport and consumer acceptance.

## Scope

This checkpoint records the successful authenticated live path:

`MT4 -> K_AI native MARKET_CONTEXT schema 1.1 -> bounded loopback HTTP -> restricted reverse SSH -> 127.0.0.1:18765 -> K-Trader validator`

It does not authorize provider activation, strategy changes, risk/execution changes, broker actions or holdout access.

## Producer contract

Authoritative K_AI native-M15 implementation: `kolemasakar/K_AI-Trading-System`.

Native-M15 implementation commit: `4ac4e5d5e3b35d6fb0dc2dda252e1b8eb0241b72`.

Delivery implementation commits:

- boundary: `3e7895e9e74f0f4f9728e92d35ad6b26626a344f`;
- service: `160713e3bdf31010b994a8e515e58820d58b8c90`;
- acceptance/docs: `1c3c9e4eaf0611e28ac4e8ee430e05c19413c13e`.

Canonical live contract: schema `1.1`, exact scopes `D1/H1/M15/M5`, depths `60/200/300/300`, native MT4 `PERIOD_M15`, closed bars only, strict chronology and unique timestamps.

Timestamp semantics: `BrokerServer` + `BROKER_SERVER_WALL_CLOCK_OPAQUE` + `utc_offset_minutes=null`.

## Transport acceptance

K_AI local listener: `127.0.0.1:8765`.

K-Trader-side restricted reverse-SSH listener: `127.0.0.1:18765`.

Authentication: HTTP Bearer token from protected runtime secret `KAI_MARKET_CONTEXT_DELIVERY_TOKEN`.

The token value is not stored in repository content. GitHub Actions exposed it to the workflow as a masked secret and logs recorded `***`, not the credential.

## Live workflow result

Workflow: `K_AI MT4 Live E2E`.

Workflow run id: `35236593165`.

Tested K-Trader commit: `a84796cabcf9c8279da589a8f3cd8a6897c91a65`.

Job: `live-e2e` — `success`.

Successful steps included isolated E2E runtime bootstrap, bounded transport health verification, live schema 1.1 acquisition/acceptance and artifact upload.

Live acquisition run_id: `MCTXDELIVERY_20260917_175430_125595_02F8FF75`.

Symbol/market: `ETHUSDt / crypto`.

Acceptance result: `PASS`.

Verified payload facts:

- source `MT4`;
- producer schema `1.1`;
- scopes exactly `D1/H1/M15/M5`;
- depths `D1=60`, `H1=200`, `M15=300`, `M5=300`;
- `closed_bars_only=true`;
- `time_source=BrokerServer`;
- `timestamp_semantics=BROKER_SERVER_WALL_CLOCK_OPAQUE`;
- `utc_offset_minutes=null`;
- credential_logged=false;
- transport `bounded_loopback_http_over_restricted_reverse_ssh`.

## Fail-closed validation

Negative contract smoke: `6/6 PASS`.

Cases:

- schema `1.0` rejected when M15 required;
- M15 depth mismatch rejected;
- timestamp semantics violation rejected;
- non-null UTC offset rejected;
- duplicate M15 timestamp rejected;
- current bar not after latest closed bar rejected.

## Safety result

`provider_registered=false`

`production_activation=false`

`trading_authorized=false`

No strategy/risk/execution path was activated by this acceptance.

## Artifact

Artifact name: `kai-mt4-http-e2e-acceptance`.

Artifact id: `10503249469`.

Artifact ZIP SHA-256: `130e148b8a1a79dea6f0dbe6b77eb9cab052be41124289a59033c93aba7847b1`.

## Decision

`KAI_MARKET_CONTEXT_TRANSPORT = PASS`

`AUTHENTICATED_ACQUIRE = PASS`

`KAI_KTRADER_LIVE_E2E = PASS`

`NEGATIVE_FAIL_CLOSED = 6/6 PASS`

`PRODUCTION_PROVIDER_ACTIVATION = NOT AUTHORIZED`

The integration transport/E2E implementation task is complete. The delivery service, reverse-SSH tunnel, K-Trader loopback endpoint and protected secret remain active while K-Trader needs the channel.

Merge of PR #60 and any future `kai_mt4` provider activation are separate decisions and must not be inferred from this checkpoint.
