# Test Plan v1.3

## Test layers

1. Unit tests
- normalization
- candle boundary/OHLCV validation
- gap and freshness logic
- storage round-trip/upsert/provenance/migration
- live WebSocket payload parsing
- local MTF aggregation
- True Range / Wilder ATR14
- ATR5D valid-bar filter
- SMA/EMA and MA50/200
- volume/relative-volume/relative-spread
- generic ATR-used metric
- levels/trap/VSA state logic
- scoring hard filters

2. Provider contract tests
- same normalized interface for each adapter
- capability declarations
- historical fetch
- live candle stream contract where testable

3. Historical bootstrap tests
- required closed-bar depth
- current/open candle exclusion
- canonical 1d/4h/1h/15m/5m coverage
- missing-bar rejection
- stale-history rejection
- no partial MTF persistence on failure
- repeat bootstrap idempotency

4. Live market-data tests
- Binance and Bybit kline normalization
- open candle remains provisional and is not persisted as closed history
- provider-confirmed closed 5m persistence
- complete 5m -> 15m/1h/4h/1d aggregation
- aggregate provenance
- duplicate closed-event idempotency
- stale-state detection
- reconnect policy behavior where deterministically testable
- REST reconciliation of recent closed bars
- gap-triggered REST recovery
- schema v1 -> v2 migration

5. Replay tests
- deterministic sequences for VSA/trap/levels
- missing/stale bars
- provider reconnect/gap reconciliation

6. Integration tests
- provider -> validation -> storage -> engine -> API
- source/freshness propagation
- NO TRADE fail-closed behavior

7. Deployment tests
- container build/start
- persistence across restart
- health endpoint
- CI/CD smoke test
- target-VPS REST provider and historical-bootstrap acceptance
- target-VPS public WebSocket smoke and reconnect/gap-recovery acceptance

## Mandatory acceptance cases

- Two provider adapters pass common contract tests before Phase 1 implementation exit.
- Cross-provider OHLCV mixing is rejected.
- SQLite file uses WAL mode in deployment.
- Decimal candle values round-trip without float conversion.
- Misaligned UTC candle boundaries are rejected.
- Missing historical bars are rejected, not interpolated.
- Stale bootstrap data is rejected.
- Failed MTF bootstrap writes no partial candle snapshot.
- Open live candles cannot masquerade as closed history.
- Local parent aggregation requires complete child coverage.
- Provider/native and locally aggregated candles remain distinguishable.
- Live base-interval gap triggers REST recovery or fails closed.
- Duplicate closed events remain idempotent.
- Indicator inputs must be closed and contiguous.
- ATR5D cannot replace or duplicate rejected D1 bars.
- Relative volume/spread baselines exclude the current bar.
- ATR-used exactly 40% and 80% are ACCEPTABLE; above 80% is LATE_REJECT.
- Stale data cannot emit a tradable signal.
- RR < 3 is rejected.
- ATR used > 80% is rejected.
- Unconfirmed floating level cannot validate a setup.
- Context-free VSA cannot validate a setup.
- B/C never emits tradable LONG/SHORT.
- Missing account/risk data produces position size/risk N/A.
- Restart does not enable analysis before data-readiness validation.

## Current deterministic verification

- Phase 1 provider contract suite: 7 passed.
- Phase 2 deterministic harness: 9 passed plus compileall PASS.
- Phase 3 deterministic harness: 10 passed plus compileall PASS.
- Phase 4 deterministic harness: 12 passed plus compileall PASS.

Repository-wide CI and real provider/VPS acceptance are separate later acceptance gates and are not implied by these deterministic suites.

## Fixtures

Synthetic fixtures are allowed only inside tests and must be clearly marked as test data. Production/live outputs may never substitute synthetic data for missing exchange data.
