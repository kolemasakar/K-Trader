# Phase 3 Checkpoint

Date: 2026-08-23

Status: IMPLEMENTATION COMPLETE / TARGET-VPS LIVE ACCEPTANCE PENDING.

## Implemented

- provider-independent live candle event contract;
- generic JSON WebSocket transport;
- Binance USD-M public kline WebSocket adapter;
- Bybit Linear public kline WebSocket adapter;
- Bybit application heartbeat baseline;
- normalized open/closed 5m candle parsing;
- open candle held in memory and excluded from canonical closed persistence;
- closed 5m persistence;
- complete UTC aggregation from 5m to 15m/1h/4h/1d;
- storage provenance for provider-native versus locally aggregated candles;
- SQLite schema migration v1 to v2;
- periodic REST reconciliation;
- gap-triggered REST recovery;
- stale-state detection;
- exponential reconnect baseline;
- duplicate closed-event idempotency;
- public WebSocket smoke utility for the target VPS.

## Verification

Phase 3 deterministic harness:

- 10 tests passed;
- Python compileall PASS.

Covered cases:

- Binance kline normalization;
- Bybit kline normalization and confirm/open state;
- 15m aggregation with volume/trade/taker fields;
- aggregate source provenance;
- open candle not persisted;
- closed candle persistence and parent aggregation;
- provider REST reconciliation replacing aggregate data;
- live 5m gap recovery;
- stale-state boundary;
- SQLite schema v1 to v2 migration;
- duplicate closed event idempotency.

Repository-wide CI is still deferred to the CI/CD phase and is not claimed as complete.

## Pending target-VPS acceptance

After VPS provisioning:

1. run public REST provider smoke;
2. run historical MTF bootstrap smoke;
3. run `scripts/ws_smoke.py` for an accessible provider;
4. verify continuous 5m stream reception;
5. verify persisted closed bars and parent aggregation;
6. force/test reconnect and REST gap recovery;
7. verify data remains fresh for the intended runtime window.

Offline/synthetic tests are not accepted as proof of real provider reachability or 24/7 readiness.
