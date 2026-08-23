# Test Plan v1.7

## Test layers

1. Unit tests
- normalization/candle integrity
- gap/freshness/storage/live aggregation
- ATR/MA/volume metrics
- market structure/sessions/levels
- trap/VSA evidence
- setup discovery/geometry/scoring/risk

2. Provider contract tests
- equivalent normalized interface per adapter
- historical/live public market-data contract

3. Historical bootstrap tests
- closed depth, UTC alignment, gaps/staleness, atomic persistence

4. Live market-data tests
- provisional open bar isolation
- closed 5m persistence
- complete parent aggregation
- reconnect/stale/reconciliation/gap recovery

5. Market-structure tests
- swing/regime/strength/session/level lifecycle

6. Trap/VSA replay tests
- failed-break/return/confirmation
- ND/NS/T/UT/BC/SC/SV raw detection
- HTF/location/confirmation hard filters

7. Trading Engine tests
- UTC-day range begins at 00:00 UTC
- partial-day ATR-used context is rejected
- setup candidate discovery
- evidence identity and setup-type consistency
- strong primary-level hard gate
- directional HTF hard gate
- tick-rounded Entry/Luft/SL/TP geometry
- nearest structural opposing target
- no structural target rejection
- canonical ATR-used origin
- RR >=3 hard gate
- ATR used <=80 hard gate
- deterministic component scoring
- A+/A/B/C thresholds
- hard-reject score cap / C override
- explicit RiskContext sizing and N/A without context
- LONG/SHORT only for A/A+ without rejects
- best-decision ordering

8. API tests
- health and scanner readiness separation
- all application routes are GET-only
- Decimal values preserve exact text representation
- UTC timestamp serialization
- canonical symbol/provider ambiguity -> HTTP 409
- explicit provider resolution
- candle `provider|aggregate` provenance
- candle tail/limit behavior
- per-symbol best TradingDecision serialization
- candidate list includes audit NO_TRADE/B/C outcomes
- `/v1/signals` exposes only A/A+ LONG/SHORT
- invalid interval/grade validation
- rate limit -> HTTP 429 + Retry-After
- OpenAPI operation IDs remain stable

9. Runtime coordinator tests - Phase 8.5
- provider selection/fallback without cross-provider fusion
- universe shortlist publication
- bootstrap readiness gate before analysis
- per-symbol exception isolation
- indicator/structure/Trap/VSA/engine orchestration order
- no TradingDecision on stale/gapped/incomplete input
- scanner cycle status transitions
- candidate/signal publication to `ApiReadModel`
- repeated cycles replace current snapshots deterministically
- graceful shutdown/restart boundary

10. Integration tests
- provider -> validation -> storage -> indicators -> structure -> trap/VSA -> Trading Engine -> runtime coordinator -> API
- source/freshness propagation
- fail-closed NO_TRADE behavior

11. Deployment tests
- container build/start
- persistence across restart
- scanner coordinator + API health
- repository-wide CI/CD smoke
- target-VPS REST/bootstrap/WebSocket acceptance

## Mandatory acceptance cases

- Cross-provider OHLCV mixing is rejected.
- Stale/gapped/open data cannot masquerade as confirmed analysis input.
- Failed MTF bootstrap writes no partial snapshot.
- ATR5D cannot replace/duplicate rejected D1 bars.
- MA alone cannot create directional market regime.
- Session cannot independently permit a trade.
- FLOATING/BROKEN/INVALIDATED levels cannot validate a primary setup.
- Primary tradable level must be STRONG.
- Trap requires break -> return -> confirmation.
- Context-free/unconfirmed VSA cannot validate a setup.
- Evidence identity mismatch is rejected.
- Daily ATR-used context must begin at 00:00 UTC.
- No structural target -> NO_TRADE; synthetic 3R target is prohibited.
- RR <3 is rejected.
- ATR used >80% is rejected.
- Hard reject cannot retain A/A+ public grade/score.
- B/C never emits tradable LONG/SHORT.
- Missing account/risk inputs produce position size/risk N/A.
- API cannot expose write/trading operations.
- Ambiguous multi-provider symbol cannot be silently resolved.
- API must not recalculate/override TradingDecision fields.
- Autonomous runtime must not publish analysis before data readiness.

## Current deterministic verification

- Phase 1 provider suite: 7 passed.
- Phase 2 isolated harness: 9 passed; compileall PASS.
- Phase 3 isolated harness: 10 passed; compileall PASS.
- Phase 4 isolated harness: 12 passed; compileall PASS.
- Phase 5 isolated harness: 12 passed; compile validation PASS.
- Phase 6 isolated harness: 14 passed; compile validation PASS.
- Phase 7 exact-module isolated harness: 17 passed; syntax compilation PASS.
- Phase 8 isolated API harness: 7 passed; FastAPI/OpenAPI generation and syntax validation PASS.

Repository-wide pytest/CI and real provider/VPS acceptance remain separate Phase 9 gates.

## Fixtures

Synthetic fixtures are allowed only inside tests and must be explicitly test data. Production/live outputs may never substitute synthetic data for missing exchange data.
