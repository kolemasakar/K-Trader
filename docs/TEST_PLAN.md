# Test Plan v1.1

## Test layers

1. Unit tests
- normalization
- candle boundary/OHLCV validation
- gap and freshness logic
- storage round-trip/upsert
- ATR/MA
- levels/trap/VSA state logic
- scoring hard filters

2. Provider contract tests
- same normalized interface for each adapter
- capability declarations
- historical fetch
- live subscription/reconnect where testable

3. Historical bootstrap tests
- required closed-bar depth
- current/open candle exclusion
- canonical 1d/4h/1h/15m/5m coverage
- missing-bar rejection
- stale-history rejection
- no partial MTF persistence on failure
- repeat bootstrap idempotency

4. Replay tests
- deterministic sequences for VSA/trap/levels
- missing/stale bars
- provider reconnect/gap reconciliation

5. Integration tests
- provider -> validation -> storage -> engine -> API
- source/freshness propagation
- NO TRADE fail-closed behavior

6. Deployment tests
- container build/start
- persistence across restart
- health endpoint
- CI/CD smoke test
- target-VPS provider and historical-bootstrap acceptance

## Mandatory acceptance cases

- Two provider adapters pass common contract tests before Phase 1 implementation exit.
- Cross-provider OHLCV mixing is rejected.
- SQLite file uses WAL mode in deployment.
- Decimal candle values round-trip without float conversion.
- Misaligned UTC candle boundaries are rejected.
- Missing historical bars are rejected, not interpolated.
- Stale bootstrap data is rejected.
- Failed MTF bootstrap writes no partial candle snapshot.
- Stale data cannot emit a tradable signal.
- RR < 3 is rejected.
- ATR used > 80% is rejected.
- Unconfirmed floating level cannot validate a setup.
- Context-free VSA cannot validate a setup.
- B/C never emits tradable LONG/SHORT.
- Missing account/risk data produces position size/risk N/A.
- Restart does not enable analysis before data-readiness validation.

## Fixtures

Synthetic fixtures are allowed only inside tests and must be clearly marked as test data. Production/live outputs may never substitute synthetic data for missing exchange data.
