# Test Plan v1.0

## Test layers

1. Unit tests
- normalization
- candle validation/resampling
- ATR/MA
- levels/trap/VSA state logic
- scoring hard filters

2. Provider contract tests
- same normalized interface for each adapter
- capability declarations
- historical fetch
- live subscription/reconnect where testable

3. Replay tests
- deterministic sequences for VSA/trap/levels
- missing/stale bars
- provider reconnect/gap reconciliation

4. Integration tests
- provider -> storage -> engine -> API
- source/freshness propagation
- NO TRADE fail-closed behavior

5. Deployment tests
- container build/start
- persistence across restart
- health endpoint
- CI/CD smoke test

## Mandatory acceptance cases

- Two provider adapters pass common contract tests before Phase 1 exit.
- Cross-provider OHLCV mixing is rejected.
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
