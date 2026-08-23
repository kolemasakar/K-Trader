# Test Plan v1.4

## Test layers

1. Unit tests
- normalization and candle integrity
- gap/freshness logic
- storage round-trip/upsert/provenance/migration
- live WebSocket parsing and MTF aggregation
- True Range / Wilder ATR14 / ATR5D
- SMA/EMA and MA50/200
- volume/relative-volume/relative-spread
- swing detection and regime classification
- session context and DST behavior
- level clustering/lifecycle/MTF lookup
- trap/VSA state logic
- scoring hard filters

2. Provider contract tests
- equivalent normalized interface per adapter
- capability declarations
- historical fetch
- live candle contract where testable

3. Historical bootstrap tests
- required closed-bar depth
- open candle exclusion
- canonical MTF coverage
- gap/stale rejection
- atomic persistence
- repeat bootstrap idempotency

4. Live market-data tests
- Binance/Bybit normalization
- open candle provisional only
- closed 5m persistence
- complete 5m -> 15m/1h/4h/1d aggregation
- source provenance
- reconnect/stale/reconciliation/gap recovery
- duplicate event idempotency

5. Market-structure tests
- strict swing highs/lows
- bullish/bearish/range/mixed regime cases
- MTF precedence and conflicting HTF behavior
- strength evidence counting
- configurable participation threshold
- DST-aware Tokyo/London/New York windows
- historical level clustering
- floating level exclusion
- touch-based strength
- confirmed break transition
- broken level inactive behavior
- mirror retest/confirmation
- mirror invalidation
- consolidation detection
- nearest confirmed MTF support/resistance
- explicit LIMIT/PARANORMAL_BAR evidence handling

6. Replay tests
- deterministic trap/VSA/levels sequences
- missing/stale bars
- provider reconnect/gap reconciliation

7. Integration tests
- provider -> validation -> storage -> indicators -> structure -> engine -> API
- source/freshness propagation
- NO TRADE fail-closed behavior

8. Deployment tests
- container build/start
- persistence across restart
- health endpoint
- CI/CD smoke test
- target-VPS REST/bootstrap/WebSocket acceptance

## Mandatory acceptance cases

- Cross-provider OHLCV mixing is rejected.
- Stale/gapped/open data cannot masquerade as confirmed analysis input.
- Failed MTF bootstrap writes no partial snapshot.
- Local parent aggregation requires complete child coverage.
- ATR5D cannot replace/duplicate rejected D1 bars.
- Relative-volume/spread baselines exclude current bar.
- ATR used >80% is rejected; exact 40/80% remain acceptable boundaries.
- MA alone cannot create directional market regime.
- Conflicting HTF context cannot be silently promoted to directional regime.
- Session context cannot independently permit a trade.
- FLOATING/BROKEN/INVALIDATED levels cannot act as active primary validation levels.
- Mirror becomes active only after defined retest confirmation.
- LIMIT/PARANORMAL_BAR automatic geometry is not fabricated without a versioned rule.
- Context-free VSA cannot validate a setup.
- RR <3 is rejected.
- B/C never emits tradable LONG/SHORT.
- Missing account/risk inputs produce position size/risk N/A.

## Current deterministic verification

- Phase 1 provider suite: 7 passed.
- Phase 2 deterministic harness: 9 passed; compileall PASS.
- Phase 3 deterministic harness: 10 passed; compileall PASS.
- Phase 4 deterministic harness: 12 passed; compileall PASS.
- Phase 5 local isolated harness: 12 passed; syntax/compile validation PASS.

Repository-wide CI and real provider/VPS acceptance remain separate Phase 9 gates.

## Fixtures

Synthetic fixtures are allowed only inside tests and must be clearly marked as test data. Production/live outputs may never substitute synthetic data for missing exchange data.
