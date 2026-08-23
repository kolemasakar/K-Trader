# Runtime Scanner Specification v1.0

## Purpose

Phase 8.5 composes the already implemented provider, market-data, indicator, structure, Trap/VSA, Trading Engine and API modules into one autonomous read-only scanner runtime.

Canonical flow:

provider priority/fallback -> ranked universe -> data readiness/bootstrap -> live 5m maintenance -> indicators -> MTF structure/levels/session -> Trap/VSA -> Trading Engine -> atomic ApiReadModel publication.

## Provider and universe cycle

Each scanner cycle re-evaluates provider priority through the existing provider fallback contract and refreshes the ranked universe from confirmed public market data.

A cycle uses exactly one provider. If provider selection changes, the next published snapshot fully replaces the previous provider snapshot; cross-provider state is never fused.

Canonical runtime defaults:

- universe max candidates: 50;
- analysis shortlist: top 20 by normalized liquidity;
- scan interval: 60 seconds;
- bootstrap concurrency: 2 symbols;
- setup interval: 5m.

All are operational defaults except the canonical Phase 8.5 setup interval, and must remain configurable at deployment.

## Data readiness

For every shortlisted symbol, the runtime requires the Phase 2 history plan:

- 1d: 250 closed bars;
- 4h: 250;
- 1h: 250;
- 15m: 250;
- 5m: 300.

If any required series is missing or stale, the existing atomic MTF bootstrap service is invoked. After bootstrap/live maintenance, every series is revalidated as closed, chronological, contiguous and fresh before analysis.

A failed symbol is isolated from the rest of the scanner cycle. It is not represented as a valid TradingDecision.

## Live maintenance

The coordinator owns one `LiveMarketDataService` task for the selected provider and current analysis shortlist.

The live subscription is retained between cycles and restarted only when:

- selected provider changes;
- shortlisted instrument set changes;
- runtime shuts down/restarts.

Phase 3 reconnect, reconciliation and local 5m -> 15m/1h/4h/1d aggregation rules remain authoritative.

## Analysis composition

For each ready symbol the runtime performs:

1. validated MTF history load;
2. 5m ATR14 and D1 ATR5D;
3. MTF market structure/levels/session snapshot;
4. 5m trap detection against active MTF levels;
5. 5m VSA detection and HTF/location/confirmation validation;
6. setup candidate discovery;
7. current UTC-day range construction from closed 5m bars starting at 00:00 UTC;
8. Phase 7 candidate evaluation/scoring/risk rules.

No new trading rule is introduced by the coordinator.

## NO_SETUP sentinel

A fully valid/fresh symbol may have no confirmed setup candidate. In that case the runtime publishes an explicit read-only decision sentinel:

- side: `NO_TRADE`;
- grade: `C`;
- setup score/raw score: 0;
- setup type: `NO_SETUP`;
- Entry/SL/TP/RR: null;
- primary level: null;
- reason: `NO_CONFIRMED_SETUP`.

`NO_SETUP` is not a tradable setup type and can never enter `/v1/signals`.

If mandatory market data itself is unavailable/stale/invalid, no sentinel is fabricated; the symbol fails closed and is reported through runtime failure counts/error status.

## Atomic API publication

`ApiReadModel.publish_cycle()` replaces, under one lock:

- scanner status;
- current universe;
- candle series;
- analyses;
- ranked decisions.

This prevents readers from observing a new provider universe together with stale decisions/candles from the previous provider.

On total provider/runtime failure, runtime market/decision data is cleared and status becomes `ERROR` with `data_ready=false`.

## Candle provenance

Runtime candle-series provenance may be:

- `provider`;
- `aggregate`;
- `mixed`.

`mixed` is used when a retained series includes provider-native bootstrap history plus locally aggregated live parent bars. It never means cross-provider mixing.

## Runtime status

Scanner status includes:

- provider_id;
- universe_size;
- data_ready;
- cycle_id;
- symbols_ready;
- symbols_failed;
- live_streaming;
- last_scan_at;
- last_cycle_duration_seconds;
- last_error.

A cycle with at least one ready symbol and one failed symbol is `DEGRADED`, not `READY`.

## Process entrypoint

Production runtime entrypoint:

`uvicorn ktrader.runtime.app:app`

The app starts the coordinator in the FastAPI process and performs clean coordinator/provider/repository shutdown.

Environment overrides currently supported by the runtime entrypoint:

- `KTRADER_PROVIDERS`
- `KTRADER_DB_PATH`
- `KTRADER_QUOTE_ASSET`
- `KTRADER_PRICE_LIMIT_ENABLED`
- `KTRADER_MAX_PRICE`
- `KTRADER_MAX_CANDIDATES`
- `KTRADER_ANALYSIS_LIMIT`
- `KTRADER_SCAN_INTERVAL_SECONDS`
- `KTRADER_BOOTSTRAP_CONCURRENCY`

Phase 9 deployment will map canonical deployment configuration to these runtime settings.

## Safety boundary

The runtime contains no order/account credentials, trading mutations or execution path. It only reads public exchange market data, computes analysis and serves read-only state.
